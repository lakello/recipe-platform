import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.photo import RecipePhoto


class PhotoRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_recipe(self, recipe_id: uuid.UUID) -> RecipePhoto | None:
        result = await self.session.execute(
            select(RecipePhoto).where(RecipePhoto.recipe_id == recipe_id)
        )
        return result.scalar_one_or_none()

    async def upsert(
        self, recipe_id: uuid.UUID, key: str, content_type: str
    ) -> RecipePhoto:
        existing = await self.get_by_recipe(recipe_id)
        if existing:
            existing.key = key
            existing.content_type = content_type
        else:
            existing = RecipePhoto(
                recipe_id=recipe_id, key=key, content_type=content_type
            )
            self.session.add(existing)
        await self.session.commit()
        await self.session.refresh(existing)
        return existing

    async def delete(self, photo: RecipePhoto) -> None:
        await self.session.delete(photo)
        await self.session.commit()
