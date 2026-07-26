import uuid
from datetime import datetime

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.photo import RecipePhoto, UploadIntent


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

    async def create_intent(self, intent: UploadIntent) -> UploadIntent:
        self.session.add(intent)
        await self.session.commit()
        await self.session.refresh(intent)
        return intent

    async def get_intent(self, upload_id: uuid.UUID) -> UploadIntent | None:
        result = await self.session.execute(
            select(UploadIntent).where(UploadIntent.id == upload_id)
        )
        return result.scalar_one_or_none()

    async def set_intent_status(self, intent: UploadIntent, status: str) -> None:
        intent.status = status
        await self.session.commit()

    async def delete_stale_intents(self, before: datetime) -> list[UploadIntent]:
        result = await self.session.execute(
            select(UploadIntent).where(
                UploadIntent.expires_at < before,
                UploadIntent.status.in_(("pending", "validating", "failed")),
            )
        )
        intents = list(result.scalars().all())
        if intents:
            await self.session.execute(
                delete(UploadIntent).where(
                    UploadIntent.id.in_(intent.id for intent in intents)
                )
            )
            await self.session.commit()
        return intents
