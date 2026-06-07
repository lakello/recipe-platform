import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.like import Favorite, Like


class LikeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, user_id: uuid.UUID, recipe_id: uuid.UUID) -> Like | None:
        result = await self.session.execute(
            select(Like).where(Like.user_id == user_id, Like.recipe_id == recipe_id)
        )
        return result.scalar_one_or_none()

    async def add(self, user_id: uuid.UUID, recipe_id: uuid.UUID) -> Like:
        like = Like(user_id=user_id, recipe_id=recipe_id)
        self.session.add(like)
        await self.session.commit()
        return like

    async def remove(self, like: Like) -> None:
        await self.session.delete(like)
        await self.session.commit()

    async def count(self, recipe_id: uuid.UUID) -> int:
        result = await self.session.execute(
            select(func.count()).where(Like.recipe_id == recipe_id)
        )
        return result.scalar_one()

    async def count_batch(self, recipe_ids: list[uuid.UUID]) -> dict[uuid.UUID, int]:
        if not recipe_ids:
            return {}
        result = await self.session.execute(
            select(Like.recipe_id, func.count().label("cnt"))
            .where(Like.recipe_id.in_(recipe_ids))
            .group_by(Like.recipe_id)
        )
        return {row.recipe_id: row.cnt for row in result}

    async def user_liked_batch(
        self, user_id: uuid.UUID, recipe_ids: list[uuid.UUID]
    ) -> set[uuid.UUID]:
        if not recipe_ids:
            return set()
        result = await self.session.execute(
            select(Like.recipe_id).where(
                Like.user_id == user_id, Like.recipe_id.in_(recipe_ids)
            )
        )
        return {row.recipe_id for row in result}


class FavoriteRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, user_id: uuid.UUID, recipe_id: uuid.UUID) -> Favorite | None:
        result = await self.session.execute(
            select(Favorite).where(
                Favorite.user_id == user_id, Favorite.recipe_id == recipe_id
            )
        )
        return result.scalar_one_or_none()

    async def add(self, user_id: uuid.UUID, recipe_id: uuid.UUID) -> Favorite:
        favorite = Favorite(user_id=user_id, recipe_id=recipe_id)
        self.session.add(favorite)
        await self.session.commit()
        return favorite

    async def remove(self, favorite: Favorite) -> None:
        await self.session.delete(favorite)
        await self.session.commit()

    async def list_by_user(self, user_id: uuid.UUID) -> list[uuid.UUID]:
        result = await self.session.execute(
            select(Favorite.recipe_id)
            .where(Favorite.user_id == user_id)
            .order_by(Favorite.created_at.desc())
        )
        return [row.recipe_id for row in result]

    async def user_favorited_batch(
        self, user_id: uuid.UUID, recipe_ids: list[uuid.UUID]
    ) -> set[uuid.UUID]:
        if not recipe_ids:
            return set()
        result = await self.session.execute(
            select(Favorite.recipe_id).where(
                Favorite.user_id == user_id, Favorite.recipe_id.in_(recipe_ids)
            )
        )
        return {row.recipe_id for row in result}
