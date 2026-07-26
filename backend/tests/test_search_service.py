import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException
from opensearchpy.exceptions import ConnectionError as OpenSearchConnectionError

from app.core.opensearch import (
    RECIPE_INDEX,
    RECIPE_INDEX_VERSION,
    ensure_index_exists,
)
from app.models.recipe import Difficulty, RecipeStatus, RecipeVisibility
from app.schemas.search import SearchParams
from app.services.search import SearchService


def make_service():
    client = AsyncMock()
    return SearchService(client), client


@pytest.mark.asyncio
async def test_index_bootstrap_creates_version_and_alias():
    client = AsyncMock()
    client.indices.exists_alias.return_value = False
    client.indices.exists.side_effect = [False, False]

    await ensure_index_exists(client)

    client.indices.create.assert_awaited_once()
    client.indices.put_alias.assert_awaited_once_with(
        index=RECIPE_INDEX_VERSION, name=RECIPE_INDEX
    )


def make_recipe(
    *,
    status=RecipeStatus.published,
    visibility=RecipeVisibility.public,
    category_id=None,
    cooking_time=None,
    difficulty=None,
):
    recipe = MagicMock()
    recipe.id = uuid.uuid4()
    recipe.status = status
    recipe.visibility = visibility
    recipe.title = "Test Recipe"
    recipe.description = "A test"
    recipe.author_id = uuid.uuid4()
    recipe.author.username = "chef"
    recipe.category_id = category_id
    recipe.category = MagicMock(name="Pasta") if category_id else None
    recipe.cooking_time_minutes = cooking_time
    recipe.difficulty = difficulty
    recipe.photo = None
    recipe.likes_count = 0
    recipe.created_at.isoformat.return_value = "2025-01-01T00:00:00"
    recipe.updated_at.isoformat.return_value = "2025-01-01T00:00:00"
    recipe.ingredients = []
    return recipe


@pytest.mark.asyncio
async def test_index_published_public_recipe():
    service, client = make_service()
    recipe = make_recipe()

    await service.index_recipe(recipe)

    client.index.assert_awaited_once()
    call_kwargs = client.index.call_args
    assert call_kwargs.kwargs["id"] == str(recipe.id)


@pytest.mark.asyncio
async def test_index_draft_recipe_removes_from_index():
    service, client = make_service()
    recipe = make_recipe(status=RecipeStatus.draft)
    client.delete.side_effect = None

    await service.index_recipe(recipe)

    client.index.assert_not_awaited()
    client.delete.assert_awaited_once()


@pytest.mark.asyncio
async def test_index_private_recipe_removes_from_index():
    service, client = make_service()
    recipe = make_recipe(visibility=RecipeVisibility.private)
    client.delete.side_effect = None

    await service.index_recipe(recipe)

    client.index.assert_not_awaited()
    client.delete.assert_awaited_once()


@pytest.mark.asyncio
async def test_remove_recipe_ignores_not_found():
    from opensearchpy import NotFoundError

    service, client = make_service()
    client.delete.side_effect = NotFoundError(404, "not found", {})

    await service.remove_recipe(uuid.uuid4())  # should not raise


@pytest.mark.asyncio
async def test_index_recipe_does_not_mask_unexpected_error():
    service, client = make_service()
    client.index.side_effect = Exception("connection refused")
    recipe = make_recipe()

    with pytest.raises(Exception, match="connection refused"):
        await service.index_recipe(recipe)


@pytest.mark.asyncio
async def test_search_returns_ids():
    service, client = make_service()
    rid1, rid2 = uuid.uuid4(), uuid.uuid4()
    client.search.return_value = {
        "hits": {
            "total": {"value": 2},
            "hits": [{"_id": str(rid1)}, {"_id": str(rid2)}],
        }
    }

    ids, total, cursor = await service.search(SearchParams(q="pasta"))

    assert total == 2
    assert ids == [rid1, rid2]
    assert cursor is None


@pytest.mark.asyncio
async def test_search_with_filters_builds_correct_query():
    service, client = make_service()
    client.search.return_value = {"hits": {"total": {"value": 0}, "hits": []}}
    cid = uuid.uuid4()

    await service.search(
        SearchParams(
            category_id=cid,
            max_time=30,
            difficulty=Difficulty.easy,
            sort="newest",
        )
    )

    body = client.search.call_args.kwargs["body"]
    bool_q = body["query"]["bool"]
    filters = bool_q["filter"]
    filter_keys = [list(f.keys())[0] for f in filters]
    assert "term" in filter_keys
    assert "range" in filter_keys
    assert body["sort"] == [{"created_at": "desc"}, {"_id": "asc"}]


@pytest.mark.asyncio
async def test_search_with_exclude_ingredients():
    service, client = make_service()
    client.search.return_value = {"hits": {"total": {"value": 0}, "hits": []}}

    await service.search(SearchParams(exclude_ingredients=["pork", "beef"]))

    body = client.search.call_args.kwargs["body"]
    must_not = body["query"]["bool"].get("must_not", [])
    assert len(must_not) == 2


@pytest.mark.asyncio
async def test_search_returns_503_after_transient_retries(monkeypatch):
    service, client = make_service()
    client.search.side_effect = OpenSearchConnectionError(503, "opensearch down", {})
    monkeypatch.setattr("app.services.search.asyncio.sleep", AsyncMock())

    with pytest.raises(HTTPException) as exc:
        await service.search(SearchParams(q="anything"))

    assert exc.value.status_code == 503
    assert client.search.await_count == 3


@pytest.mark.asyncio
async def test_search_after_cursor_is_forwarded():
    service, client = make_service()
    recipe_id = uuid.uuid4()
    client.search.return_value = {
        "hits": {
            "total": {"value": 2},
            "hits": [
                {
                    "_id": str(recipe_id),
                    "sort": ["2026-01-01T00:00:00", str(recipe_id)],
                }
            ],
        }
    }
    cursor_values = ["2025-01-01T00:00:00", str(uuid.uuid4())]

    await service.search(
        SearchParams(sort="newest", size=1, search_after=cursor_values)
    )

    body = client.search.call_args.kwargs["body"]
    assert body["search_after"] == cursor_values
    assert "from" not in body
