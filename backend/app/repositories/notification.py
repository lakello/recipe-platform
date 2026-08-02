import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification


class NotificationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, notification: Notification) -> Notification:
        self.session.add(notification)
        await self.session.commit()
        await self.session.refresh(notification)
        return notification

    async def get_by_id(self, notification_id: uuid.UUID) -> Notification | None:
        result = await self.session.execute(
            select(Notification).where(Notification.id == notification_id)
        )
        return result.scalar_one_or_none()

    async def get_for_email_delivery(
        self, notification_id: uuid.UUID
    ) -> Notification | None:
        result = await self.session.execute(
            select(Notification)
            .where(Notification.id == notification_id)
            .with_for_update()
        )
        return result.scalar_one_or_none()

    async def mark_email_sent(self, notification: Notification) -> None:
        notification.email_sent_at = datetime.now(UTC)
        await self.session.flush()

    async def list_for_user(
        self, user_id: uuid.UUID, offset: int, size: int
    ) -> tuple[list[Notification], int]:
        total = (
            await self.session.execute(
                select(func.count()).where(Notification.user_id == user_id)
            )
        ).scalar_one()
        rows = (
            (
                await self.session.execute(
                    select(Notification)
                    .where(Notification.user_id == user_id)
                    .order_by(Notification.created_at.desc())
                    .offset(offset)
                    .limit(size)
                )
            )
            .scalars()
            .all()
        )
        return list(rows), total

    async def mark_read(self, notification: Notification) -> Notification:
        notification.is_read = True
        await self.session.commit()
        await self.session.refresh(notification)
        return notification

    async def mark_all_read(self, user_id: uuid.UUID) -> None:
        await self.session.execute(
            update(Notification)
            .where(Notification.user_id == user_id, Notification.is_read.is_(False))
            .values(is_read=True)
        )
        await self.session.commit()

    async def count_unread(self, user_id: uuid.UUID) -> int:
        return (
            await self.session.execute(
                select(func.count()).where(
                    Notification.user_id == user_id,
                    Notification.is_read.is_(False),
                )
            )
        ).scalar_one()
