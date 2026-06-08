import uuid
from datetime import date, timedelta

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models.meal_plan import MealPlan, MealPlanItem
from app.models.shopping_list import ShoppingList, ShoppingListItem


class ShoppingListRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_list(self, user_id: uuid.UUID) -> ShoppingList | None:
        result = await self.session.execute(
            select(ShoppingList).where(ShoppingList.user_id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_or_create_list(self, user_id: uuid.UUID) -> ShoppingList:
        sl = await self.get_list(user_id)
        if sl:
            return sl
        sl = ShoppingList(user_id=user_id)
        self.session.add(sl)
        await self.session.commit()
        await self.session.refresh(sl)
        return sl

    async def get_item(self, item_id: uuid.UUID) -> ShoppingListItem | None:
        result = await self.session.execute(
            select(ShoppingListItem)
            .options(joinedload(ShoppingListItem.shopping_list))
            .where(ShoppingListItem.id == item_id)
        )
        return result.scalar_one_or_none()

    async def get_item_by_ingredient(
        self, shopping_list_id: uuid.UUID, ingredient_id: uuid.UUID
    ) -> ShoppingListItem | None:
        result = await self.session.execute(
            select(ShoppingListItem).where(
                ShoppingListItem.shopping_list_id == shopping_list_id,
                ShoppingListItem.ingredient_id == ingredient_id,
            )
        )
        return result.scalar_one_or_none()

    async def add_item(
        self,
        shopping_list_id: uuid.UUID,
        name: str,
        ingredient_id: uuid.UUID | None = None,
        amount: float | None = None,
        unit: str | None = None,
        is_manual: bool = False,
    ) -> ShoppingListItem:
        item = ShoppingListItem(
            shopping_list_id=shopping_list_id,
            ingredient_id=ingredient_id,
            name=name,
            amount=amount,
            unit=unit,
            is_manual=is_manual,
        )
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def update_item(self, item: ShoppingListItem, data: dict) -> ShoppingListItem:
        for key, value in data.items():
            setattr(item, key, value)
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def delete_item(self, item: ShoppingListItem) -> None:
        await self.session.delete(item)
        await self.session.commit()

    async def update_generated_at(self, sl: ShoppingList) -> None:
        from datetime import UTC, datetime

        sl.last_generated_at = datetime.now(UTC)
        await self.session.commit()

    async def get_meal_plan_items_for_dates(
        self, user_id: uuid.UUID, dates: list[date]
    ) -> list[MealPlanItem]:
        if not dates:
            return []

        week_map: dict[date, list[int]] = {}
        for d in dates:
            ws = d - timedelta(days=d.weekday())
            week_map.setdefault(ws, []).append(d.weekday())

        conditions = or_(
            *[
                and_(
                    MealPlan.week_start == ws,
                    MealPlanItem.day_of_week.in_(dows),
                )
                for ws, dows in week_map.items()
            ]
        )

        result = await self.session.execute(
            select(MealPlanItem)
            .join(MealPlan, MealPlanItem.meal_plan_id == MealPlan.id)
            .where(MealPlan.user_id == user_id)
            .where(conditions)
        )
        return list(result.scalars().all())
