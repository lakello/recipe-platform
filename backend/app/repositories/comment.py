import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.comment import Comment


class CommentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, comment: Comment) -> Comment:
        self.session.add(comment)
        await self.session.commit()
        await self.session.refresh(comment)
        return comment

    async def get_by_id(self, comment_id: uuid.UUID) -> Comment | None:
        result = await self.session.execute(
            select(Comment).where(Comment.id == comment_id)
        )
        return result.scalar_one_or_none()

    async def list_top_level(
        self, recipe_id: uuid.UUID, offset: int, limit: int
    ) -> tuple[list[Comment], int]:
        base = select(Comment).where(
            Comment.recipe_id == recipe_id,
            Comment.parent_id.is_(None),
        )
        total_result = await self.session.execute(
            select(func.count()).select_from(base.subquery())
        )
        total = total_result.scalar_one()
        result = await self.session.execute(
            base.order_by(Comment.created_at.asc()).offset(offset).limit(limit)
        )
        return list(result.scalars().all()), total

    async def list_replies(
        self, parent_id: uuid.UUID, offset: int, limit: int
    ) -> tuple[list[Comment], int]:
        base = select(Comment).where(Comment.parent_id == parent_id)
        total_result = await self.session.execute(
            select(func.count()).select_from(base.subquery())
        )
        total = total_result.scalar_one()
        result = await self.session.execute(
            base.order_by(Comment.created_at.asc()).offset(offset).limit(limit)
        )
        return list(result.scalars().all()), total

    async def update(self, comment: Comment, data: dict[str, object]) -> Comment:
        for key, value in data.items():
            setattr(comment, key, value)
        await self.session.commit()
        await self.session.refresh(comment)
        return comment

    async def reply_count_batch(
        self, comment_ids: list[uuid.UUID]
    ) -> dict[uuid.UUID, int]:
        if not comment_ids:
            return {}
        result = await self.session.execute(
            select(Comment.parent_id, func.count().label("cnt"))
            .where(Comment.parent_id.in_(comment_ids))
            .group_by(Comment.parent_id)
        )
        return {row.parent_id: row.cnt for row in result}
