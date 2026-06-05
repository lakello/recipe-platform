import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException

from app.models.ingredient import (
    Ingredient,
    IngredientUnit,
    RecipeIngredient,
    RecipeStep,
)
from app.models.recipe import Recipe, RecipeStatus, RecipeVisibility
from app.repositories.ingredient import IngredientRepository
from app.repositories.recipe import RecipeRepository
from app.schemas.ingredient import RecipeIngredientItem, RecipeStepItem
from app.services.ingredient import IngredientService


def make_recipe(author_id: uuid.UUID | None = None, **kwargs) -> Recipe:
    author_id = author_id or uuid.uuid4()
    recipe = MagicMock(spec=Recipe)
    recipe.id = uuid.uuid4()
    recipe.author_id = author_id
    recipe.status = RecipeStatus.draft
    recipe.visibility = RecipeVisibility.public
    recipe.title = "Test"
    recipe.description = None
    recipe.cooking_time_minutes = None
    recipe.servings = None
    recipe.difficulty = None
    recipe.category_id = None
    recipe.category = None
    recipe.ingredients = []
    recipe.steps = []
    recipe.created_at = datetime.now(UTC)
    recipe.updated_at = datetime.now(UTC)
    for k, v in kwargs.items():
        setattr(recipe, k, v)
    return recipe


def make_ingredient(name: str = "Мука") -> Ingredient:
    ing = MagicMock(spec=Ingredient)
    ing.id = uuid.uuid4()
    ing.name = name
    ing.created_at = datetime.now(UTC)
    return ing


def make_recipe_ingredient(ingredient: Ingredient, order: int = 0) -> RecipeIngredient:
    ri = MagicMock(spec=RecipeIngredient)
    ri.id = uuid.uuid4()
    ri.ingredient_id = ingredient.id
    ri.ingredient = ingredient
    ri.amount = 200.0
    ri.unit = IngredientUnit.g  # noqa: E741
    ri.order = order
    return ri


def make_step(order: int = 0) -> RecipeStep:
    step = MagicMock(spec=RecipeStep)
    step.id = uuid.uuid4()
    step.order = order
    step.title = None
    step.description = "Смешать"
    return step


@pytest.fixture
def ingredient_repo() -> AsyncMock:
    return AsyncMock(spec=IngredientRepository)


@pytest.fixture
def recipe_repo() -> AsyncMock:
    return AsyncMock(spec=RecipeRepository)


@pytest.fixture
def service(ingredient_repo: AsyncMock, recipe_repo: AsyncMock) -> IngredientService:
    return IngredientService(ingredient_repo, recipe_repo)


async def test_search_ingredients(
    service: IngredientService, ingredient_repo: AsyncMock
) -> None:
    ingredient_repo.search.return_value = [
        make_ingredient("Мука"),
        make_ingredient("Молоко"),
    ]
    result = await service.search_ingredients("м")
    assert len(result) == 2
    ingredient_repo.search.assert_called_once_with("м")


async def test_set_ingredients_success(
    service: IngredientService,
    ingredient_repo: AsyncMock,
    recipe_repo: AsyncMock,
) -> None:
    author_id = uuid.uuid4()
    recipe = make_recipe(author_id=author_id)
    recipe_repo.get_by_id.return_value = recipe
    recipe_repo.session = AsyncMock()

    items = [
        RecipeIngredientItem(ingredient_name="Мука", amount=200, unit=IngredientUnit.g)
    ]
    await service.set_ingredients(recipe.id, author_id, items)

    ingredient_repo.replace_recipe_ingredients.assert_called_once()


async def test_set_ingredients_wrong_author(
    service: IngredientService,
    ingredient_repo: AsyncMock,
    recipe_repo: AsyncMock,
) -> None:
    recipe = make_recipe()
    recipe_repo.get_by_id.return_value = recipe

    with pytest.raises(HTTPException) as exc:
        await service.set_ingredients(recipe.id, uuid.uuid4(), [])
    assert exc.value.status_code == 403


async def test_set_ingredients_recipe_not_found(
    service: IngredientService,
    ingredient_repo: AsyncMock,
    recipe_repo: AsyncMock,
) -> None:
    recipe_repo.get_by_id.return_value = None

    with pytest.raises(HTTPException) as exc:
        await service.set_ingredients(uuid.uuid4(), uuid.uuid4(), [])
    assert exc.value.status_code == 404


async def test_set_steps_success(
    service: IngredientService,
    ingredient_repo: AsyncMock,
    recipe_repo: AsyncMock,
) -> None:
    author_id = uuid.uuid4()
    recipe = make_recipe(author_id=author_id)
    recipe_repo.get_by_id.return_value = recipe
    recipe_repo.session = AsyncMock()

    items = [
        RecipeStepItem(description="Нагреть масло"),
        RecipeStepItem(description="Добавить лук"),
    ]
    await service.set_steps(recipe.id, author_id, items)

    ingredient_repo.replace_recipe_steps.assert_called_once()


async def test_set_steps_wrong_author(
    service: IngredientService,
    ingredient_repo: AsyncMock,
    recipe_repo: AsyncMock,
) -> None:
    recipe = make_recipe()
    recipe_repo.get_by_id.return_value = recipe

    with pytest.raises(HTTPException) as exc:
        await service.set_steps(recipe.id, uuid.uuid4(), [])
    assert exc.value.status_code == 403
