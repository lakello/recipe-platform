import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.models.recipe import Difficulty, Recipe, RecipeStatus, RecipeVisibility
from app.repositories.recipe import RecipeRepository
from app.schemas.recipe import RecipeCreate, RecipeUpdate
from app.services.recipe import RecipeService


def make_recipe(**kwargs) -> Recipe:
    author_id = kwargs.pop("author_id", uuid.uuid4())
    defaults = {
        "id": uuid.uuid4(),
        "author_id": author_id,
        "title": "Test Recipe",
        "description": None,
        "status": RecipeStatus.published,
        "visibility": RecipeVisibility.public,
        "cooking_time_minutes": None,
        "servings": None,
        "difficulty": None,
        "category_id": None,
        "category": None,
        "photo": None,
        "ingredients": [],
        "steps": [],
        "created_at": datetime.now(UTC),
        "updated_at": datetime.now(UTC),
    }
    defaults.update(kwargs)
    recipe = MagicMock(spec=Recipe)
    for key, value in defaults.items():
        setattr(recipe, key, value)
    return recipe


@pytest.fixture
def repo() -> AsyncMock:
    return AsyncMock(spec=RecipeRepository)


@pytest.fixture
def service(repo: AsyncMock) -> RecipeService:
    return RecipeService(repo)


async def test_create_recipe(service: RecipeService, repo: AsyncMock) -> None:
    author_id = uuid.uuid4()
    repo.create.return_value = make_recipe(author_id=author_id)

    data = RecipeCreate(title="Борщ", visibility=RecipeVisibility.public)
    result = await service.create_recipe(data, author_id)

    assert result.title == "Test Recipe"
    repo.create.assert_called_once()


async def test_get_recipe_public(service: RecipeService, repo: AsyncMock) -> None:
    recipe = make_recipe(
        status=RecipeStatus.published, visibility=RecipeVisibility.public
    )
    repo.get_by_id.return_value = recipe

    result = await service.get_recipe(recipe.id, current_user_id=None)
    assert result.id == recipe.id


async def test_get_recipe_private_by_author(
    service: RecipeService, repo: AsyncMock
) -> None:
    author_id = uuid.uuid4()
    recipe = make_recipe(
        author_id=author_id,
        status=RecipeStatus.published,
        visibility=RecipeVisibility.private,
    )
    repo.get_by_id.return_value = recipe

    result = await service.get_recipe(recipe.id, current_user_id=author_id)
    assert result.id == recipe.id


async def test_get_recipe_private_by_other_user(
    service: RecipeService, repo: AsyncMock
) -> None:
    recipe = make_recipe(
        status=RecipeStatus.published, visibility=RecipeVisibility.private
    )
    repo.get_by_id.return_value = recipe

    with pytest.raises(HTTPException) as exc:
        await service.get_recipe(recipe.id, current_user_id=uuid.uuid4())

    assert exc.value.status_code == 404


async def test_get_recipe_deleted(service: RecipeService, repo: AsyncMock) -> None:
    recipe = make_recipe(status=RecipeStatus.deleted)
    repo.get_by_id.return_value = recipe

    with pytest.raises(HTTPException) as exc:
        await service.get_recipe(recipe.id, current_user_id=None)

    assert exc.value.status_code == 404


async def test_update_recipe_by_author(service: RecipeService, repo: AsyncMock) -> None:
    author_id = uuid.uuid4()
    recipe = make_recipe(author_id=author_id)
    updated = make_recipe(author_id=author_id, title="Updated")
    repo.get_by_id.return_value = recipe
    repo.update.return_value = updated

    data = RecipeUpdate(title="Updated")
    result = await service.update_recipe(recipe.id, data, author_id)

    assert result.title == "Updated"


async def test_update_recipe_by_other_user(
    service: RecipeService, repo: AsyncMock
) -> None:
    recipe = make_recipe()
    repo.get_by_id.return_value = recipe

    data = RecipeUpdate(title="Hacked")
    with pytest.raises(HTTPException) as exc:
        await service.update_recipe(recipe.id, data, uuid.uuid4())

    assert exc.value.status_code == 403


async def test_delete_recipe_by_author(service: RecipeService, repo: AsyncMock) -> None:
    author_id = uuid.uuid4()
    recipe = make_recipe(author_id=author_id)
    repo.get_by_id.return_value = recipe

    await service.delete_recipe(recipe.id, author_id)
    repo.delete.assert_called_once_with(recipe)


async def test_delete_recipe_by_other_user(
    service: RecipeService, repo: AsyncMock
) -> None:
    recipe = make_recipe()
    repo.get_by_id.return_value = recipe

    with pytest.raises(HTTPException) as exc:
        await service.delete_recipe(recipe.id, uuid.uuid4())

    assert exc.value.status_code == 403


async def test_list_recipes_unauthenticated(
    service: RecipeService, repo: AsyncMock
) -> None:
    repo.list_visible.return_value = [make_recipe()]

    result = await service.list_recipes(current_user_id=None)

    assert len(result) == 1
    repo.list_visible.assert_called_once_with(None, None)


async def test_create_recipe_with_all_fields(
    service: RecipeService, repo: AsyncMock
) -> None:
    author_id = uuid.uuid4()
    repo.create.return_value = make_recipe(
        author_id=author_id,
        title="Паста",
        cooking_time_minutes=30,
        servings=4,
        difficulty=Difficulty.easy,
    )

    data = RecipeCreate(
        title="Паста",
        cooking_time_minutes=30,
        servings=4,
        difficulty=Difficulty.easy,
    )
    result = await service.create_recipe(data, author_id)

    assert result.cooking_time_minutes == 30
    assert result.servings == 4
    assert result.difficulty == Difficulty.easy
