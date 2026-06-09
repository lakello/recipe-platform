import logging

from opensearchpy import AsyncOpenSearch

from app.core.config import settings

logger = logging.getLogger(__name__)

RECIPE_INDEX = "recipes"

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
    exists = await client.indices.exists(index=RECIPE_INDEX)
    if not exists:
        await client.indices.create(index=RECIPE_INDEX, body=RECIPE_INDEX_MAPPING)
        logger.info("Created OpenSearch index: %s", RECIPE_INDEX)
