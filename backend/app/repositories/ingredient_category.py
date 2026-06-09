import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ingredient_category import IngredientCategory


class IngredientCategoryRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, category: IngredientCategory) -> IngredientCategory:
        self.session.add(category)
        await self.session.commit()
        await self.session.refresh(category)
        return category

    async def get_by_id(self, category_id: uuid.UUID) -> IngredientCategory | None:
        result = await self.session.execute(
            select(IngredientCategory).where(IngredientCategory.id == category_id)
        )
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> IngredientCategory | None:
        result = await self.session.execute(
            select(IngredientCategory).where(IngredientCategory.name == name)
        )
        return result.scalar_one_or_none()

    async def list_all(self) -> list[IngredientCategory]:
        result = await self.session.execute(
            select(IngredientCategory).order_by(IngredientCategory.name)
        )
        return list(result.scalars().all())

    async def update(
        self, category: IngredientCategory, data: dict[str, object]
    ) -> IngredientCategory:
        for key, value in data.items():
            setattr(category, key, value)
        await self.session.commit()
        await self.session.refresh(category)
        return category

    async def delete(self, category: IngredientCategory) -> None:
        await self.session.delete(category)
        await self.session.commit()
