import uuid
from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.meal_plan import MealPlanRepository
from app.repositories.recipe import RecipeRepository
from app.schemas.meal_plan import (
    CopyFromWeekRequest,
    CopyWeekRequest,
    MealPlanItemCreate,
    MealPlanItemRead,
    MealPlanItemUpdate,
    MealPlanRead,
)
from app.services.meal_plan import MealPlanService

router = APIRouter(prefix="/api/meal-plans", tags=["meal-plans"])


def _service(session: AsyncSession = Depends(get_db)) -> MealPlanService:
    return MealPlanService(
        MealPlanRepository(session),
        RecipeRepository(session),
    )


@router.get("/week", response_model=MealPlanRead)
async def get_week_plan(
    week_start: Annotated[date, Query()],
    service: MealPlanService = Depends(_service),
    current_user: User = Depends(get_current_user),
) -> MealPlanRead:
    return await service.get_week(current_user.id, week_start)


@router.post("/items", response_model=MealPlanItemRead, status_code=201)
async def add_item(
    data: MealPlanItemCreate,
    service: MealPlanService = Depends(_service),
    current_user: User = Depends(get_current_user),
) -> MealPlanItemRead:
    return await service.add_item(current_user.id, data)


@router.patch("/items/{item_id}", response_model=MealPlanItemRead)
async def update_item(
    item_id: uuid.UUID,
    data: MealPlanItemUpdate,
    service: MealPlanService = Depends(_service),
    current_user: User = Depends(get_current_user),
) -> MealPlanItemRead:
    return await service.update_item(current_user.id, item_id, data)


@router.delete("/items/{item_id}", status_code=204)
async def delete_item(
    item_id: uuid.UUID,
    service: MealPlanService = Depends(_service),
    current_user: User = Depends(get_current_user),
) -> None:
    await service.delete_item(current_user.id, item_id)


@router.post("/copy-next-week", response_model=MealPlanRead)
async def copy_to_next_week(
    data: CopyWeekRequest,
    service: MealPlanService = Depends(_service),
    current_user: User = Depends(get_current_user),
) -> MealPlanRead:
    return await service.copy_to_next_week(current_user.id, data)


@router.post("/copy-week", response_model=MealPlanRead)
async def copy_week(
    data: CopyFromWeekRequest,
    service: MealPlanService = Depends(_service),
    current_user: User = Depends(get_current_user),
) -> MealPlanRead:
    return await service.copy_from_week(current_user.id, data)
