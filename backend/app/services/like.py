import uuid

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.repositories.like import FavoriteRepository, LikeRepository
from app.repositories.recipe import RecipeRepository
from app.schemas.like import FavoriteStatus, LikeStatus
from app.schemas.recipe import RecipeRead


class LikeService:
    def __init__(
        self, like_repo: LikeRepository, recipe_repo: RecipeRepository
    ) -> None:
        self.like_repo = like_repo
        self.recipe_repo = recipe_repo

    async def like(self, recipe_id: uuid.UUID, user_id: uuid.UUID) -> LikeStatus:
        await self._assert_recipe_exists(recipe_id)
        existing = await self.like_repo.get(user_id, recipe_id)
        if existing:
            raise HTTPException(status_code=409, detail="Already liked")
        try:
            await self.like_repo.add(user_id, recipe_id)
            await self.like_repo.session.commit()
        except IntegrityError as exc:
            await self.like_repo.session.rollback()
            raise HTTPException(status_code=409, detail="Already liked") from exc
        count = await self.like_repo.count(recipe_id)
        return LikeStatus(likes_count=count, is_liked=True)

    async def unlike(self, recipe_id: uuid.UUID, user_id: uuid.UUID) -> LikeStatus:
        await self._assert_recipe_exists(recipe_id)
        existing = await self.like_repo.get(user_id, recipe_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Like not found")
        await self.like_repo.remove(existing)
        await self.like_repo.session.commit()
        count = await self.like_repo.count(recipe_id)
        return LikeStatus(likes_count=count, is_liked=False)

    async def get_status(
        self, recipe_id: uuid.UUID, user_id: uuid.UUID | None
    ) -> LikeStatus:
        await self._assert_recipe_exists(recipe_id)
        count = await self.like_repo.count(recipe_id)
        is_liked = False
        if user_id:
            is_liked = await self.like_repo.get(user_id, recipe_id) is not None
        return LikeStatus(likes_count=count, is_liked=is_liked)

    async def _assert_recipe_exists(self, recipe_id: uuid.UUID) -> None:
        recipe = await self.recipe_repo.get_by_id(recipe_id)
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")


class FavoriteService:
    def __init__(
        self,
        favorite_repo: FavoriteRepository,
        like_repo: LikeRepository,
        recipe_repo: RecipeRepository,
    ) -> None:
        self.favorite_repo = favorite_repo
        self.like_repo = like_repo
        self.recipe_repo = recipe_repo

    async def add_favorite(
        self, recipe_id: uuid.UUID, user_id: uuid.UUID
    ) -> FavoriteStatus:
        await self._assert_recipe_exists(recipe_id)
        existing = await self.favorite_repo.get(user_id, recipe_id)
        if existing:
            raise HTTPException(status_code=409, detail="Already in favorites")
        try:
            await self.favorite_repo.add(user_id, recipe_id)
            await self.favorite_repo.session.commit()
        except IntegrityError as exc:
            await self.favorite_repo.session.rollback()
            raise HTTPException(status_code=409, detail="Already in favorites") from exc
        return FavoriteStatus(is_favorited=True)

    async def remove_favorite(
        self, recipe_id: uuid.UUID, user_id: uuid.UUID
    ) -> FavoriteStatus:
        await self._assert_recipe_exists(recipe_id)
        existing = await self.favorite_repo.get(user_id, recipe_id)
        if not existing:
            raise HTTPException(status_code=404, detail="Favorite not found")
        await self.favorite_repo.remove(existing)
        await self.favorite_repo.session.commit()
        return FavoriteStatus(is_favorited=False)

    async def list_favorites(self, user_id: uuid.UUID) -> list[RecipeRead]:
        recipe_ids = await self.favorite_repo.list_by_user(user_id)
        if not recipe_ids:
            return []

        count_map = await self.like_repo.count_batch(recipe_ids)
        liked_set = await self.like_repo.user_liked_batch(user_id, recipe_ids)

        recipes = []
        for recipe in await self.recipe_repo.get_by_ids(recipe_ids):
            recipe_read = RecipeRead.model_validate(recipe)
            recipe_read = recipe_read.model_copy(
                update={
                    "likes_count": count_map.get(recipe.id, 0),
                    "is_liked": recipe.id in liked_set,
                    "is_favorited": True,
                }
            )
            recipes.append(recipe_read)
        return recipes

    async def _assert_recipe_exists(self, recipe_id: uuid.UUID) -> None:
        recipe = await self.recipe_repo.get_by_id(recipe_id)
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")
