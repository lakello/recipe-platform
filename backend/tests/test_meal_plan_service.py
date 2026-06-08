import uuid
from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.meal_plan import MealPlan, MealPlanItem, MealType
from app.schemas.meal_plan import (
    CopyWeekRequest,
    MealPlanItemCreate,
    MealPlanItemUpdate,
)
from app.services.meal_plan import MealPlanService

MONDAY = date(2026, 6, 8)
TUESDAY = date(2026, 6, 9)


def make_service():
    repo = AsyncMock()
    recipe_repo = AsyncMock()
    return MealPlanService(repo, recipe_repo), repo, recipe_repo


def make_plan(week_start=MONDAY, items=None):
    plan = MagicMock(spec=MealPlan)
    plan.id = uuid.uuid4()
    plan.user_id = uuid.uuid4()
    plan.week_start = week_start
    plan.items = items or []
    return plan


def make_recipe():
    recipe = MagicMock()
    recipe.id = uuid.uuid4()
    recipe.title = "Test Recipe"
    recipe.cooking_time_minutes = 30
    recipe.servings = 2
    recipe.difficulty = None
    recipe.photo = None
    recipe.category = None
    return recipe


def make_item(plan=None):
    item = MagicMock(spec=MealPlanItem)
    item.id = uuid.uuid4()
    item.day_of_week = 0
    item.meal_type = MealType.lunch
    item.recipe_id = uuid.uuid4()
    item.servings = 2
    item.meal_plan = plan or make_plan()
    item.recipe = make_recipe()
    return item


@pytest.mark.anyio
async def test_get_week_creates_plan_if_missing():
    service, repo, _ = make_service()
    plan = make_plan()
    repo.get_or_create_week_plan.return_value = plan

    result = await service.get_week(uuid.uuid4(), MONDAY)

    repo.get_or_create_week_plan.assert_awaited_once()
    assert result.week_start == MONDAY


@pytest.mark.anyio
async def test_get_week_rejects_non_monday():
    service, _, _ = make_service()

    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc:
        await service.get_week(uuid.uuid4(), TUESDAY)
    assert exc.value.status_code == 400


@pytest.mark.anyio
async def test_add_item_creates_and_returns_item():
    service, repo, recipe_repo = make_service()
    plan = make_plan()
    item = make_item(plan)
    repo.get_or_create_week_plan.return_value = plan
    repo.add_item.return_value = item
    recipe_repo.get_by_id.return_value = MagicMock()

    data = MealPlanItemCreate(
        week_start=MONDAY,
        day_of_week=0,
        meal_type=MealType.lunch,
        recipe_id=uuid.uuid4(),
        servings=2,
    )
    result = await service.add_item(uuid.uuid4(), data)

    repo.add_item.assert_awaited_once()
    assert result.servings == 2


@pytest.mark.anyio
async def test_add_item_raises_404_for_missing_recipe():
    service, _, recipe_repo = make_service()
    recipe_repo.get_by_id.return_value = None

    from fastapi import HTTPException

    data = MealPlanItemCreate(
        week_start=MONDAY,
        day_of_week=0,
        meal_type=MealType.dinner,
        recipe_id=uuid.uuid4(),
        servings=1,
    )
    with pytest.raises(HTTPException) as exc:
        await service.add_item(uuid.uuid4(), data)
    assert exc.value.status_code == 404


@pytest.mark.anyio
async def test_update_item_changes_servings():
    service, repo, _ = make_service()
    user_id = uuid.uuid4()
    plan = make_plan()
    plan.user_id = user_id
    item = make_item(plan)
    updated = make_item(plan)
    updated.servings = 4
    repo.get_item.return_value = item
    repo.update_item.return_value = updated

    result = await service.update_item(user_id, item.id, MealPlanItemUpdate(servings=4))

    repo.update_item.assert_awaited_once_with(item, 4)
    assert result.servings == 4


@pytest.mark.anyio
async def test_update_item_forbidden_for_other_user():
    service, repo, _ = make_service()
    item = make_item()  # plan.user_id is random
    repo.get_item.return_value = item

    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc:
        await service.update_item(uuid.uuid4(), item.id, MealPlanItemUpdate(servings=1))
    assert exc.value.status_code == 403


@pytest.mark.anyio
async def test_delete_item_calls_repo():
    service, repo, _ = make_service()
    user_id = uuid.uuid4()
    plan = make_plan()
    plan.user_id = user_id
    item = make_item(plan)
    repo.get_item.return_value = item

    await service.delete_item(user_id, item.id)

    repo.delete_item.assert_awaited_once_with(item)


@pytest.mark.anyio
async def test_delete_item_not_found():
    service, repo, _ = make_service()
    repo.get_item.return_value = None

    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc:
        await service.delete_item(uuid.uuid4(), uuid.uuid4())
    assert exc.value.status_code == 404


@pytest.mark.anyio
async def test_copy_to_next_week_copies_items():
    service, repo, _ = make_service()
    user_id = uuid.uuid4()
    source = make_plan(MONDAY)
    next_plan = make_plan(date(2026, 6, 15))
    repo.get_week_plan.side_effect = [source, next_plan]
    repo.get_or_create_week_plan.return_value = next_plan

    result = await service.copy_to_next_week(
        user_id, CopyWeekRequest(week_start=MONDAY)
    )

    repo.copy_items.assert_awaited_once_with(source.id, next_plan.id)
    assert result.week_start == date(2026, 6, 15)


@pytest.mark.anyio
async def test_copy_to_next_week_no_source_raises_404():
    service, repo, _ = make_service()
    repo.get_week_plan.return_value = None

    from fastapi import HTTPException

    with pytest.raises(HTTPException) as exc:
        await service.copy_to_next_week(
            uuid.uuid4(), CopyWeekRequest(week_start=MONDAY)
        )
    assert exc.value.status_code == 404
