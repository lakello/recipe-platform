import logging

from opensearchpy import AsyncOpenSearch

from app.core.config import settings

logger = logging.getLogger(__name__)

RECIPE_INDEX = "recipes-current"
RECIPE_INDEX_VERSION = "recipes-v1"
LEGACY_RECIPE_INDEX = "recipes"

RECIPE_INDEX_MAPPING = {
    "mappings": {
        "properties": {
            "title": {"type": "text", "analyzer": "standard"},
            "description": {"type": "text", "analyzer": "standard"},
            "ingredient_names": {"type": "text", "analyzer": "standard"},
            "category_id": {"type": "keyword"},
            "category_name": {"type": "keyword"},
            "cooking_time_minutes": {"type": "integer"},
            "difficulty": {"type": "keyword"},
            "status": {"type": "keyword"},
            "visibility": {"type": "keyword"},
            "author_id": {"type": "keyword"},
            "author_username": {"type": "keyword"},
            "photo_url": {"type": "keyword", "index": False},
            "likes_count": {"type": "integer"},
            "created_at": {"type": "date"},
            "updated_at": {"type": "date"},
        }
    }
}


def create_opensearch_client() -> AsyncOpenSearch:
    return AsyncOpenSearch(
        hosts=[settings.opensearch_url],
        use_ssl=False,
        verify_certs=False,
    )


async def ensure_index_exists(client: AsyncOpenSearch) -> None:
    if await client.indices.exists_alias(name=RECIPE_INDEX):
        return
    if not await client.indices.exists(index=RECIPE_INDEX_VERSION):
        await client.indices.create(
            index=RECIPE_INDEX_VERSION, body=RECIPE_INDEX_MAPPING
        )
        if await client.indices.exists(index=LEGACY_RECIPE_INDEX):
            await client.reindex(
                body={
                    "source": {"index": LEGACY_RECIPE_INDEX},
                    "dest": {"index": RECIPE_INDEX_VERSION},
                },
                wait_for_completion=True,
            )
    await client.indices.put_alias(index=RECIPE_INDEX_VERSION, name=RECIPE_INDEX)
    logger.info(
        "OpenSearch alias %s points to %s",
        RECIPE_INDEX,
        RECIPE_INDEX_VERSION,
    )
