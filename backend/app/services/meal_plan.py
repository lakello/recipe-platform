import uuid
from datetime import date, timedelta

from fastapi import HTTPException

from app.models.meal_plan import MealPlanItem
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


class MealPlanService:
    def __init__(self, repo: MealPlanRepository, recipe_repo: RecipeRepository) -> None:
        self.repo = repo
        self.recipe_repo = recipe_repo

    def _require_monday(self, week_start: date) -> None:
        if week_start.weekday() != 0:
            raise HTTPException(
                status_code=400, detail="week_start must be a Monday (weekday 0)"
            )

    async def get_week(self, user_id: uuid.UUID, week_start: date) -> MealPlanRead:
        self._require_monday(week_start)
        plan = await self.repo.get_or_create_week_plan(user_id, week_start)
        return MealPlanRead.model_validate(plan)

    async def add_item(
        self, user_id: uuid.UUID, data: MealPlanItemCreate
    ) -> MealPlanItemRead:
        self._require_monday(data.week_start)
        recipe = await self.recipe_repo.get_by_id(data.recipe_id)
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")
        plan = await self.repo.get_or_create_week_plan(user_id, data.week_start)
        item = await self.repo.add_item(
            plan.id, data.recipe_id, data.day_of_week, data.meal_type, data.servings
        )
        return MealPlanItemRead.model_validate(item)

    async def update_item(
        self, user_id: uuid.UUID, item_id: uuid.UUID, data: MealPlanItemUpdate
    ) -> MealPlanItemRead:
        item = await self._get_owned_item(user_id, item_id)
        item = await self.repo.update_item(item, data.servings)
        return MealPlanItemRead.model_validate(item)

    async def delete_item(self, user_id: uuid.UUID, item_id: uuid.UUID) -> None:
        item = await self._get_owned_item(user_id, item_id)
        await self.repo.delete_item(item)

    async def copy_to_next_week(
        self, user_id: uuid.UUID, data: CopyWeekRequest
    ) -> MealPlanRead:
        self._require_monday(data.week_start)
        source = await self.repo.get_week_plan(user_id, data.week_start)
        if not source:
            raise HTTPException(status_code=404, detail="No plan for this week")
        next_monday = data.week_start + timedelta(weeks=1)
        target = await self.repo.get_or_create_week_plan(user_id, next_monday)
        await self.repo.copy_items(source.id, target.id)
        updated = await self.repo.get_week_plan(user_id, next_monday)
        return MealPlanRead.model_validate(updated)

    async def copy_from_week(
        self, user_id: uuid.UUID, data: CopyFromWeekRequest
    ) -> MealPlanRead:
        self._require_monday(data.source_week_start)
        self._require_monday(data.target_week_start)
        source = await self.repo.get_week_plan(user_id, data.source_week_start)
        if not source:
            raise HTTPException(status_code=404, detail="No plan for source week")
        target = await self.repo.get_or_create_week_plan(
            user_id, data.target_week_start
        )
        await self.repo.copy_items(source.id, target.id)
        updated = await self.repo.get_week_plan(user_id, data.target_week_start)
        return MealPlanRead.model_validate(updated)

    async def _get_owned_item(
        self, user_id: uuid.UUID, item_id: uuid.UUID
    ) -> MealPlanItem:
        item = await self.repo.get_item(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        if item.meal_plan.user_id != user_id:
            raise HTTPException(status_code=403, detail="Forbidden")
        return item
