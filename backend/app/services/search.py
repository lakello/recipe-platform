import logging
import uuid

from opensearchpy import AsyncOpenSearch, NotFoundError

from app.core.opensearch import RECIPE_INDEX
from app.models.recipe import RecipeStatus, RecipeVisibility
from app.schemas.recipe import RecipeRead
from app.schemas.search import SearchParams

logger = logging.getLogger(__name__)


class SearchService:
    def __init__(self, client: AsyncOpenSearch) -> None:
        self.client = client

    async def index_recipe(self, recipe: RecipeRead) -> None:
        if (
            recipe.status != RecipeStatus.published
            or recipe.visibility != RecipeVisibility.public
        ):
            await self.remove_recipe(recipe.id)
            return

        doc = {
            "title": recipe.title,
            "description": recipe.description or "",
            "ingredient_names": [i.ingredient.name for i in recipe.ingredients],
            "category_id": str(recipe.category_id) if recipe.category_id else None,
            "category_name": recipe.category.name if recipe.category else None,
            "cooking_time_minutes": recipe.cooking_time_minutes,
            "difficulty": recipe.difficulty,
            "status": recipe.status,
            "visibility": recipe.visibility,
            "author_id": str(recipe.author_id),
            "author_username": recipe.author.username,
            "photo_url": recipe.photo.key if recipe.photo else None,
            "likes_count": recipe.likes_count,
            "created_at": recipe.created_at.isoformat(),
            "updated_at": recipe.updated_at.isoformat(),
        }

        try:
            await self.client.index(
                index=RECIPE_INDEX,
                id=str(recipe.id),
                body=doc,
            )
        except Exception as exc:
            logger.warning("Failed to index recipe %s: %s", recipe.id, exc)

    async def remove_recipe(self, recipe_id: uuid.UUID) -> None:
        try:
            await self.client.delete(index=RECIPE_INDEX, id=str(recipe_id))
        except NotFoundError:
            pass
        except Exception as exc:
            logger.warning("Failed to remove recipe %s from index: %s", recipe_id, exc)

    async def search(self, params: SearchParams) -> tuple[list[uuid.UUID], int]:
        must_clauses: list[dict] = []
        filter_clauses: list[dict] = [
            {"term": {"status": "published"}},
            {"term": {"visibility": "public"}},
        ]
        must_not_clauses: list[dict] = []

        if params.q:
            must_clauses.append(
                {
                    "multi_match": {
                        "query": params.q,
                        "fields": ["title^3", "description", "ingredient_names^2"],
                        "type": "best_fields",
                        "fuzziness": "AUTO",
                    }
                }
            )

        if params.category_id:
            filter_clauses.append({"term": {"category_id": str(params.category_id)}})

        range_filter: dict = {}
        if params.min_time:
            range_filter["gte"] = params.min_time
        if params.max_time:
            range_filter["lte"] = params.max_time
        if range_filter:
            filter_clauses.append({"range": {"cooking_time_minutes": range_filter}})

        if params.difficulty:
            filter_clauses.append({"term": {"difficulty": params.difficulty}})

        for ingredient in params.include_ingredients:
            filter_clauses.append({"match": {"ingredient_names": ingredient}})

        for ingredient in params.exclude_ingredients:
            must_not_clauses.append({"match": {"ingredient_names": ingredient}})

        bool_query: dict = {"filter": filter_clauses}
        if must_clauses:
            bool_query["must"] = must_clauses
        if must_not_clauses:
            bool_query["must_not"] = must_not_clauses

        sort: list
        if params.sort == "newest":
            sort = [{"created_at": "desc"}]
        elif params.sort == "popular":
            sort = [{"likes_count": "desc"}, {"created_at": "desc"}]
        else:
            sort = ["_score", {"created_at": "desc"}]

        try:
            response = await self.client.search(
                index=RECIPE_INDEX,
                body={
                    "query": {"bool": bool_query},
                    "sort": sort,
                    "from": (params.page - 1) * params.size,
                    "size": params.size,
                    "_source": False,
                },
            )
        except Exception as exc:
            logger.warning("Search failed: %s", exc)
            return [], 0

        total = response["hits"]["total"]["value"]
        ids = [uuid.UUID(hit["_id"]) for hit in response["hits"]["hits"]]
        return ids, total
