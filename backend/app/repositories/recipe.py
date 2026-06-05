import uuid

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.recipe import Recipe, RecipeStatus, RecipeVisibility


class RecipeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, recipe: Recipe) -> Recipe:
        self.session.add(recipe)
        await self.session.commit()
        await self.session.refresh(recipe)
        return recipe

    async def get_by_id(self, recipe_id: uuid.UUID) -> Recipe | None:
        result = await self.session.execute(
            select(Recipe).where(Recipe.id == recipe_id)
        )
        return result.scalar_one_or_none()

    async def list_visible(self, current_user_id: uuid.UUID | None) -> list[Recipe]:
        if current_user_id:
            stmt = select(Recipe).where(
                or_(
                    and_(
                        Recipe.status == RecipeStatus.published,
                        Recipe.visibility == RecipeVisibility.public,
                    ),
                    and_(
                        Recipe.author_id == current_user_id,
                        Recipe.status != RecipeStatus.deleted,
                    ),
                )
            )
        else:
            stmt = select(Recipe).where(
                Recipe.status == RecipeStatus.published,
                Recipe.visibility == RecipeVisibility.public,
            )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, recipe: Recipe, data: dict) -> Recipe:
        for key, value in data.items():
            setattr(recipe, key, value)
        await self.session.commit()
        await self.session.refresh(recipe)
        return recipe

    async def delete(self, recipe: Recipe) -> None:
        recipe.status = RecipeStatus.deleted
        await self.session.commit()
