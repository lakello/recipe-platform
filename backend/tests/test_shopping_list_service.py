"""Tests for shopping list generation algorithm (normalize/denormalize/smart merge)."""

import uuid
from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.services.shopping_list import (
    ShoppingListService,
    _dates_for_mode,
    denormalize_amount,
    normalize_amount,
)

# --- Pure function tests ---


def test_normalize_kg_to_g():
    assert normalize_amount(1.5, "kg") == (1500.0, "g")


def test_normalize_l_to_ml():
    assert normalize_amount(2.0, "l") == (2000.0, "ml")


def test_normalize_g_unchanged():
    assert normalize_amount(500.0, "g") == (500.0, "g")


def test_normalize_pcs_unchanged():
    assert normalize_amount(3.0, "pcs") == (3.0, "pcs")


def test_denormalize_g_to_kg_when_large():
    amount, unit = denormalize_amount(1500.0, "g")
    assert unit == "kg"
    assert abs(amount - 1.5) < 0.001


def test_denormalize_ml_to_l_when_large():
    amount, unit = denormalize_amount(2000.0, "ml")
    assert unit == "l"
    assert abs(amount - 2.0) < 0.001


def test_denormalize_g_stays_when_small():
    amount, unit = denormalize_amount(500.0, "g")
    assert unit == "g"
    assert amount == 500.0


def test_dates_for_today():
    result = _dates_for_mode("today", None)
    assert len(result) == 1
    assert result[0] == date.today()


def test_dates_for_week():
    result = _dates_for_mode("week", None)
    assert len(result) == 7
    assert result[0] == date.today()


def test_dates_for_custom():
    custom = [date(2026, 6, 8), date(2026, 6, 10)]
    result = _dates_for_mode("custom", custom)
    assert result == custom


def test_dates_for_custom_no_dates_raises():
    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc:
        _dates_for_mode("custom", None)
    assert exc.value.status_code == 400


# --- Smart merge tests ---


def _make_shopping_list():
    sl = MagicMock()
    sl.id = uuid.uuid4()
    sl.last_generated_at = None
    sl.items = []
    return sl


def _make_repo(existing_item=None):
    repo = AsyncMock()
    sl = _make_shopping_list()
    repo.get_or_create_list.return_value = sl
    repo.get_list.return_value = sl
    repo.get_meal_plan_items_for_dates.return_value = []
    repo.get_item_by_ingredient.return_value = existing_item
    repo.add_item.return_value = MagicMock()
    repo.update_item.return_value = MagicMock()
    return repo


def _make_meal_item(ingredient_id, ingredient_name, amount, unit_value, servings=1):
    ingredient = MagicMock()
    ingredient.id = ingredient_id
    ingredient.name = ingredient_name

    ri = MagicMock()
    ri.ingredient_id = ingredient_id
    ri.ingredient = ingredient
    ri.amount = amount
    ri.unit = MagicMock(value=unit_value) if unit_value else None

    recipe = MagicMock()
    recipe.ingredients = [ri]

    mp_item = MagicMock()
    mp_item.recipe = recipe
    mp_item.servings = servings
    return mp_item


@pytest.mark.anyio
async def test_generate_adds_new_item():
    """Generated item not in list → added."""
    ing_id = uuid.uuid4()
    repo = _make_repo(existing_item=None)
    repo.get_meal_plan_items_for_dates.return_value = [
        _make_meal_item(ing_id, "Морковь", 500, "g")
    ]
    svc = ShoppingListService(repo)

    from app.schemas.shopping_list import GenerateRequest

    await svc.generate(uuid.uuid4(), GenerateRequest(mode="today"))
    repo.add_item.assert_called_once()
    call_kwargs = repo.add_item.call_args
    assert call_kwargs.args[1] == "Морковь"
    assert call_kwargs.kwargs["amount"] == 500.0
    assert call_kwargs.kwargs["unit"] == "g"


@pytest.mark.anyio
async def test_generate_skips_when_existing_sufficient():
    """Existing 1kg >= generated 500g → no update."""
    ing_id = uuid.uuid4()
    existing = MagicMock()
    existing.amount = 1.0
    existing.unit = "kg"
    repo = _make_repo(existing_item=existing)
    repo.get_meal_plan_items_for_dates.return_value = [
        _make_meal_item(ing_id, "Картофель", 500, "g")
    ]
    svc = ShoppingListService(repo)

    from app.schemas.shopping_list import GenerateRequest

    await svc.generate(uuid.uuid4(), GenerateRequest(mode="today"))
    repo.add_item.assert_not_called()
    repo.update_item.assert_not_called()


@pytest.mark.anyio
async def test_generate_updates_when_existing_insufficient():
    """Existing 500g < generated 1kg → update to 1kg."""
    ing_id = uuid.uuid4()
    existing = MagicMock()
    existing.amount = 500.0
    existing.unit = "g"
    repo = _make_repo(existing_item=existing)
    repo.get_meal_plan_items_for_dates.return_value = [
        _make_meal_item(ing_id, "Макароны", 1, "kg")
    ]
    svc = ShoppingListService(repo)

    from app.schemas.shopping_list import GenerateRequest

    await svc.generate(uuid.uuid4(), GenerateRequest(mode="today"))
    repo.update_item.assert_called_once()
    updated_data = repo.update_item.call_args.args[1]
    assert updated_data["unit"] == "kg"
    assert abs(updated_data["amount"] - 1.0) < 0.01


@pytest.mark.anyio
async def test_generate_multiplies_servings():
    """Recipe has 200g, servings=3 → aggregated 600g."""
    ing_id = uuid.uuid4()
    repo = _make_repo(existing_item=None)
    repo.get_meal_plan_items_for_dates.return_value = [
        _make_meal_item(ing_id, "Рис", 200, "g", servings=3)
    ]
    svc = ShoppingListService(repo)

    from app.schemas.shopping_list import GenerateRequest

    await svc.generate(uuid.uuid4(), GenerateRequest(mode="today"))
    repo.add_item.assert_called_once()
    kwargs = repo.add_item.call_args.kwargs
    assert kwargs["amount"] == 600.0
    assert kwargs["unit"] == "g"


@pytest.mark.anyio
async def test_generate_aggregates_same_ingredient():
    """Same ingredient in two meals → amounts are summed."""
    ing_id = uuid.uuid4()
    repo = _make_repo(existing_item=None)
    repo.get_meal_plan_items_for_dates.return_value = [
        _make_meal_item(ing_id, "Лук", 100, "g"),
        _make_meal_item(ing_id, "Лук", 150, "g"),
    ]
    svc = ShoppingListService(repo)

    from app.schemas.shopping_list import GenerateRequest

    await svc.generate(uuid.uuid4(), GenerateRequest(mode="today"))
    repo.add_item.assert_called_once()
    kwargs = repo.add_item.call_args.kwargs
    assert kwargs["amount"] == 250.0
