import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification_preferences import NotificationPreferences


class NotificationPreferencesRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_or_default(self, user_id: uuid.UUID) -> NotificationPreferences:
        result = await self.session.execute(
            select(NotificationPreferences).where(
                NotificationPreferences.user_id == user_id
            )
        )
        prefs = result.scalar_one_or_none()
        if prefs is None:
            prefs = NotificationPreferences(user_id=user_id)
            self.session.add(prefs)
            await self.session.commit()
            await self.session.refresh(prefs)
        return prefs

    async def update(
        self, user_id: uuid.UUID, data: dict[str, bool]
    ) -> NotificationPreferences:
        prefs = await self.get_or_default(user_id)
        for key, value in data.items():
            setattr(prefs, key, value)
        await self.session.commit()
        await self.session.refresh(prefs)
        return prefs
