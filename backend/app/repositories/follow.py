import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.follow import Follow
from app.models.user import User


class FollowRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(
        self, follower_id: uuid.UUID, following_id: uuid.UUID
    ) -> Follow | None:
        result = await self.session.execute(
            select(Follow).where(
                Follow.follower_id == follower_id,
                Follow.following_id == following_id,
            )
        )
        return result.scalar_one_or_none()

    async def create(self, follower_id: uuid.UUID, following_id: uuid.UUID) -> Follow:
        follow = Follow(follower_id=follower_id, following_id=following_id)
        self.session.add(follow)
        await self.session.commit()
        await self.session.refresh(follow)
        return follow

    async def delete(self, follow: Follow) -> None:
        await self.session.delete(follow)
        await self.session.commit()

    async def count_followers(self, user_id: uuid.UUID) -> int:
        result = await self.session.execute(
            select(func.count()).where(Follow.following_id == user_id)
        )
        return result.scalar_one()

    async def count_following(self, user_id: uuid.UUID) -> int:
        result = await self.session.execute(
            select(func.count()).where(Follow.follower_id == user_id)
        )
        return result.scalar_one()

    async def list_followers(
        self, user_id: uuid.UUID, page: int, size: int
    ) -> tuple[list[User], int]:
        total_result = await self.session.execute(
            select(func.count()).where(Follow.following_id == user_id)
        )
        total = total_result.scalar_one()

        result = await self.session.execute(
            select(User)
            .join(Follow, Follow.follower_id == User.id)
            .where(Follow.following_id == user_id)
            .order_by(Follow.created_at.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        users = list(result.scalars().all())
        return users, total

    async def list_following(
        self, user_id: uuid.UUID, page: int, size: int
    ) -> tuple[list[User], int]:
        total_result = await self.session.execute(
            select(func.count()).where(Follow.follower_id == user_id)
        )
        total = total_result.scalar_one()

        result = await self.session.execute(
            select(User)
            .join(Follow, Follow.following_id == User.id)
            .where(Follow.follower_id == user_id)
            .order_by(Follow.created_at.desc())
            .offset((page - 1) * size)
            .limit(size)
        )
        users = list(result.scalars().all())
        return users, total

    async def get_following_ids(self, user_id: uuid.UUID) -> list[uuid.UUID]:
        result = await self.session.execute(
            select(Follow.following_id).where(Follow.follower_id == user_id)
        )
        return list(result.scalars().all())

    async def is_following_batch(
        self, follower_id: uuid.UUID, user_ids: list[uuid.UUID]
    ) -> set[uuid.UUID]:
        if not user_ids:
            return set()
        result = await self.session.execute(
            select(Follow.following_id).where(
                Follow.follower_id == follower_id,
                Follow.following_id.in_(user_ids),
            )
        )
        return set(result.scalars().all())
