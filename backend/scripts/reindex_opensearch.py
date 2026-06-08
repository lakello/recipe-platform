"""One-shot script: index all published public recipes into OpenSearch."""

import asyncio
import logging

import app.models.category  # noqa: F401
import app.models.comment  # noqa: F401
import app.models.follow  # noqa: F401
import app.models.ingredient  # noqa: F401
import app.models.like  # noqa: F401
import app.models.photo  # noqa: F401
import app.models.recipe  # noqa: F401
import app.models.refresh_token  # noqa: F401
import app.models.user  # noqa: F401
from app.core.opensearch import create_opensearch_client, ensure_index_exists
from app.db.session import async_session_factory
from app.repositories.comment import CommentRepository
from app.repositories.like import FavoriteRepository, LikeRepository
from app.repositories.recipe import RecipeRepository
from app.schemas.recipe import RecipeRead
from app.services.recipe import RecipeService
from app.services.search import SearchService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main() -> None:
    client = create_opensearch_client()
    await ensure_index_exists(client)
    search_service = SearchService(client)

    async with async_session_factory() as session:
        recipe_service = RecipeService(
            RecipeRepository(session),
            LikeRepository(session),
            FavoriteRepository(session),
            CommentRepository(session),
        )
        recipes: list[RecipeRead] = await recipe_service.list_recipes(
            current_user_id=None
        )

    logger.info("Found %d public published recipes to index", len(recipes))

    indexed = 0
    for recipe in recipes:
        await search_service.index_recipe(recipe)
        indexed += 1

    await client.close()
    logger.info("Done: indexed %d recipes", indexed)


if __name__ == "__main__":
    asyncio.run(main())
