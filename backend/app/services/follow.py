import uuid

from fastapi import HTTPException

from app.repositories.follow import FollowRepository
from app.repositories.user import UserRepository
from app.schemas.follow import FollowUserPage, FollowUserRead


class FollowService:
    def __init__(
        self,
        follow_repo: FollowRepository,
        user_repo: UserRepository,
    ) -> None:
        self.follow_repo = follow_repo
        self.user_repo = user_repo

    async def follow(self, follower_id: uuid.UUID, following_id: uuid.UUID) -> None:
        if follower_id == following_id:
            raise HTTPException(status_code=400, detail="Cannot follow yourself")
        target = await self.user_repo.get_by_id(following_id)
        if not target:
            raise HTTPException(status_code=404, detail="User not found")
        existing = await self.follow_repo.get(follower_id, following_id)
        if existing:
            raise HTTPException(status_code=409, detail="Already following")
        await self.follow_repo.create(follower_id, following_id)

    async def unfollow(self, follower_id: uuid.UUID, following_id: uuid.UUID) -> None:
        follow = await self.follow_repo.get(follower_id, following_id)
        if not follow:
            raise HTTPException(status_code=404, detail="Not following")
        await self.follow_repo.delete(follow)

    async def list_followers(
        self,
        user_id: uuid.UUID,
        current_user_id: uuid.UUID | None,
        page: int,
        size: int,
    ) -> FollowUserPage:
        users, total = await self.follow_repo.list_followers(user_id, page, size)
        following_set: set[uuid.UUID] = set()
        if current_user_id:
            ids = [u.id for u in users]
            following_set = await self.follow_repo.is_following_batch(
                current_user_id, ids
            )
        items = [
            FollowUserRead(
                id=u.id,
                username=u.username,
                avatar_url=u.avatar_url,
                is_following=u.id in following_set,
            )
            for u in users
        ]
        return FollowUserPage(
            items=items,
            total=total,
            page=page,
            size=size,
            has_more=(page * size) < total,
        )

    async def list_following(
        self,
        user_id: uuid.UUID,
        current_user_id: uuid.UUID | None,
        page: int,
        size: int,
    ) -> FollowUserPage:
        users, total = await self.follow_repo.list_following(user_id, page, size)
        following_set: set[uuid.UUID] = set()
        if current_user_id:
            ids = [u.id for u in users]
            following_set = await self.follow_repo.is_following_batch(
                current_user_id, ids
            )
        items = [
            FollowUserRead(
                id=u.id,
                username=u.username,
                avatar_url=u.avatar_url,
                is_following=u.id in following_set,
            )
            for u in users
        ]
        return FollowUserPage(
            items=items,
            total=total,
            page=page,
            size=size,
            has_more=(page * size) < total,
        )
