from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.moderation_action import ModerationAction


class ModerationActionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, action: ModerationAction) -> ModerationAction:
        self.session.add(action)
        await self.session.commit()
        await self.session.refresh(action)
        return action

    async def list_all(
        self, offset: int, limit: int
    ) -> tuple[list[ModerationAction], int]:
        base = select(ModerationAction)
        total_result = await self.session.execute(
            select(func.count()).select_from(base.subquery())
        )
        total = total_result.scalar_one()
        result = await self.session.execute(
            base.order_by(ModerationAction.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all()), total
