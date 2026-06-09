import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ingredient import Ingredient, RecipeIngredient, RecipeStep


class IngredientRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_or_create(self, name: str) -> Ingredient:
        name = name.strip()
        result = await self.session.execute(
            select(Ingredient).where(Ingredient.name == name)
        )
        ingredient = result.scalar_one_or_none()
        if not ingredient:
            ingredient = Ingredient(name=name)
            self.session.add(ingredient)
            await self.session.flush()
        return ingredient

    async def search(self, query: str, limit: int = 20) -> list[Ingredient]:
        result = await self.session.execute(
            select(Ingredient)
            .where(Ingredient.name.ilike(f"%{query}%"))
            .order_by(Ingredient.name)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def replace_recipe_ingredients(
        self,
        recipe_id: uuid.UUID,
        items: list[dict[str, object]],
    ) -> None:
        await self.session.execute(
            RecipeIngredient.__table__.delete().where(  # type: ignore[attr-defined]
                RecipeIngredient.recipe_id == recipe_id
            )
        )
        for order, item in enumerate(items):
            ingredient = await self.get_or_create(str(item["ingredient_name"]))
            self.session.add(
                RecipeIngredient(
                    recipe_id=recipe_id,
                    ingredient_id=ingredient.id,
                    amount=item.get("amount"),
                    unit=item.get("unit"),
                    order=order,
                )
            )
        await self.session.commit()

    async def replace_recipe_steps(
        self,
        recipe_id: uuid.UUID,
        items: list[dict[str, object]],
    ) -> None:
        await self.session.execute(
            RecipeStep.__table__.delete().where(RecipeStep.recipe_id == recipe_id)  # type: ignore[attr-defined]
        )
        for order, item in enumerate(items):
            self.session.add(
                RecipeStep(
                    recipe_id=recipe_id,
                    order=order,
                    title=item.get("title"),
                    description=item["description"],
                )
            )
        await self.session.commit()
