import asyncio
import base64
import json
import logging
import uuid
from collections.abc import Awaitable, Callable
from typing import TypeVar

from fastapi import HTTPException
from opensearchpy import AsyncOpenSearch, NotFoundError
from opensearchpy.exceptions import (
    ConnectionError as OpenSearchConnectionError,
)
from opensearchpy.exceptions import ConnectionTimeout, TransportError

from app.core.opensearch import RECIPE_INDEX
from app.models.recipe import RecipeStatus, RecipeVisibility
from app.schemas.recipe import RecipeRead
from app.schemas.search import SearchParams

logger = logging.getLogger(__name__)
T = TypeVar("T")
_RETRYABLE_STATUS = {429, 502, 503, 504}


class SearchService:
    def __init__(self, client: AsyncOpenSearch) -> None:
        self.client = client

    async def _call(self, operation: Callable[[], Awaitable[T]]) -> T:
        for attempt in range(3):
            try:
                return await operation()
            except NotFoundError:
                raise
            except (OpenSearchConnectionError, ConnectionTimeout) as exc:
                if attempt == 2:
                    raise HTTPException(
                        status_code=503, detail="Search is temporarily unavailable"
                    ) from exc
            except TransportError as exc:
                if exc.status_code not in _RETRYABLE_STATUS:
                    raise HTTPException(
                        status_code=503, detail="Search is unavailable"
                    ) from exc
                if attempt == 2:
                    raise HTTPException(
                        status_code=503, detail="Search is temporarily unavailable"
                    ) from exc
            await asyncio.sleep(0.1 * (2**attempt))
        raise AssertionError("unreachable")

    @staticmethod
    def encode_cursor(sort_values: list[object]) -> str:
        payload = json.dumps(sort_values, separators=(",", ":")).encode()
        return base64.urlsafe_b64encode(payload).decode().rstrip("=")

    @staticmethod
    def decode_cursor(cursor: str) -> list[str | int | float]:
        try:
            padding = "=" * (-len(cursor) % 4)
            values = json.loads(base64.urlsafe_b64decode(cursor + padding).decode())
            if not isinstance(values, list) or not all(
                isinstance(value, str | int | float) for value in values
            ):
                raise ValueError
            return values
        except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise HTTPException(
                status_code=422, detail="Invalid search cursor"
            ) from exc

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

        await self._call(
            lambda: self.client.index(
                index=RECIPE_INDEX,
                id=str(recipe.id),
                body=doc,
            )
        )

    async def remove_recipe(self, recipe_id: uuid.UUID) -> None:
        try:
            await self._call(
                lambda: self.client.delete(index=RECIPE_INDEX, id=str(recipe_id))
            )
        except NotFoundError:
            pass

    async def search(
        self, params: SearchParams
    ) -> tuple[list[uuid.UUID], int, str | None]:
        must_clauses: list[dict[str, object]] = []
        filter_clauses: list[dict[str, object]] = [
            {"term": {"status": "published"}},
            {"term": {"visibility": "public"}},
        ]
        must_not_clauses: list[dict[str, object]] = []

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

        range_filter: dict[str, int] = {}
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

        bool_query: dict[str, object] = {"filter": filter_clauses}
        if must_clauses:
            bool_query["must"] = must_clauses
        if must_not_clauses:
            bool_query["must_not"] = must_not_clauses

        sort: list[object]
        if params.sort == "newest":
            sort = [{"created_at": "desc"}, {"_id": "asc"}]
        elif params.sort == "popular":
            sort = [
                {"likes_count": "desc"},
                {"created_at": "desc"},
                {"_id": "asc"},
            ]
        else:
            sort = ["_score", {"created_at": "desc"}, {"_id": "asc"}]

        body: dict[str, object] = {
            "query": {"bool": bool_query},
            "sort": sort,
            "size": params.size,
            "_source": False,
        }
        if params.search_after:
            body["search_after"] = params.search_after
        else:
            body["from"] = (params.page - 1) * params.size

        response = await self._call(
            lambda: self.client.search(
                index=RECIPE_INDEX,
                body=body,
            )
        )

        total = response["hits"]["total"]["value"]
        hits = response["hits"]["hits"]
        ids = [uuid.UUID(hit["_id"]) for hit in hits]
        next_cursor = (
            self.encode_cursor(hits[-1]["sort"])
            if len(hits) == params.size and hits[-1].get("sort")
            else None
        )
        return ids, total, next_cursor
