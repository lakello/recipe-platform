import uuid
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.meal_plan import MealPlan, MealPlanItem, MealType


class MealPlanRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_week_plan(
        self, user_id: uuid.UUID, week_start: date
    ) -> MealPlan | None:
        result = await self.session.execute(
            select(MealPlan).where(
                MealPlan.user_id == user_id,
                MealPlan.week_start == week_start,
            )
        )
        return result.scalar_one_or_none()

    async def get_or_create_week_plan(
        self, user_id: uuid.UUID, week_start: date
    ) -> MealPlan:
        plan = await self.get_week_plan(user_id, week_start)
        if plan:
            return plan
        plan = MealPlan(user_id=user_id, week_start=week_start)
        self.session.add(plan)
        await self.session.commit()
        await self.session.refresh(plan)
        return plan

    async def get_item(self, item_id: uuid.UUID) -> MealPlanItem | None:
        result = await self.session.execute(
            select(MealPlanItem)
            .options(joinedload(MealPlanItem.meal_plan))
            .where(MealPlanItem.id == item_id)
        )
        return result.scalar_one_or_none()

    async def add_item(
        self,
        meal_plan_id: uuid.UUID,
        recipe_id: uuid.UUID,
        day_of_week: int,
        meal_type: MealType,
        servings: int,
    ) -> MealPlanItem:
        item = MealPlanItem(
            meal_plan_id=meal_plan_id,
            recipe_id=recipe_id,
            day_of_week=day_of_week,
            meal_type=meal_type,
            servings=servings,
        )
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def update_item(self, item: MealPlanItem, servings: int) -> MealPlanItem:
        item.servings = servings
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def delete_item(self, item: MealPlanItem) -> None:
        await self.session.delete(item)
        await self.session.commit()

    async def copy_items(
        self, source_plan_id: uuid.UUID, target_plan_id: uuid.UUID
    ) -> None:
        result = await self.session.execute(
            select(MealPlanItem).where(MealPlanItem.meal_plan_id == source_plan_id)
        )
        for item in result.scalars().all():
            self.session.add(
                MealPlanItem(
                    meal_plan_id=target_plan_id,
                    recipe_id=item.recipe_id,
                    day_of_week=item.day_of_week,
                    meal_type=item.meal_type,
                    servings=item.servings,
                )
            )
        await self.session.commit()
