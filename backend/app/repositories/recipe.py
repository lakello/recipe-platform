import uuid

from sqlalchemy import and_, func, or_, select
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

    async def list_visible(
        self,
        current_user_id: uuid.UUID | None,
        category_id: uuid.UUID | None = None,
        author_id: uuid.UUID | None = None,
    ) -> list[Recipe]:
        public_cond = and_(
            Recipe.status == RecipeStatus.published,
            Recipe.visibility == RecipeVisibility.public,
            Recipe.is_hidden.is_(False),
        )
        if current_user_id:
            stmt = select(Recipe).where(
                or_(
                    public_cond,
                    and_(
                        Recipe.author_id == current_user_id,
                        Recipe.status != RecipeStatus.deleted,
                        Recipe.is_hidden.is_(False),
                    ),
                )
            )
        else:
            stmt = select(Recipe).where(public_cond)
        if category_id is not None:
            stmt = stmt.where(Recipe.category_id == category_id)
        if author_id is not None:
            stmt = stmt.where(Recipe.author_id == author_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_all_admin(self, offset: int, limit: int) -> tuple[list[Recipe], int]:
        base = select(Recipe).where(Recipe.status != RecipeStatus.deleted)
        total_result = await self.session.execute(
            select(func.count()).select_from(base.subquery())
        )
        total = total_result.scalar_one()
        result = await self.session.execute(
            base.order_by(Recipe.created_at.desc()).offset(offset).limit(limit)
        )
        return list(result.scalars().all()), total

    async def list_feed(
        self,
        author_ids: list[uuid.UUID],
        page: int,
        size: int,
    ) -> tuple[list[Recipe], int]:
        if not author_ids:
            return [], 0
        base = (
            select(Recipe)
            .where(
                Recipe.author_id.in_(author_ids),
                Recipe.status == RecipeStatus.published,
                Recipe.visibility == RecipeVisibility.public,
            )
            .order_by(Recipe.created_at.desc())
        )
        from sqlalchemy import func

        total_result = await self.session.execute(
            select(func.count()).select_from(base.subquery())
        )
        total = total_result.scalar_one()
        result = await self.session.execute(base.offset((page - 1) * size).limit(size))
        return list(result.scalars().all()), total

    async def get_by_ids(self, ids: list[uuid.UUID]) -> list[Recipe]:
        if not ids:
            return []
        result = await self.session.execute(select(Recipe).where(Recipe.id.in_(ids)))
        recipes = {r.id: r for r in result.scalars().all()}
        return [recipes[id_] for id_ in ids if id_ in recipes]

    async def update(self, recipe: Recipe, data: dict) -> Recipe:
        for key, value in data.items():
            setattr(recipe, key, value)
        await self.session.commit()
        await self.session.refresh(recipe)
        return recipe

    async def delete(self, recipe: Recipe) -> None:
        recipe.status = RecipeStatus.deleted
        await self.session.commit()
