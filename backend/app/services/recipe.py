import uuid

from fastapi import HTTPException

from app.models.recipe import Recipe, RecipeStatus, RecipeVisibility
from app.repositories.comment import CommentRepository
from app.repositories.like import FavoriteRepository, LikeRepository
from app.repositories.recipe import RecipeRepository
from app.schemas.recipe import RecipeCreate, RecipeRead, RecipeUpdate


class RecipeService:
    def __init__(
        self,
        repository: RecipeRepository,
        like_repo: LikeRepository | None = None,
        favorite_repo: FavoriteRepository | None = None,
        comment_repo: CommentRepository | None = None,
    ) -> None:
        self.repository = repository
        self.like_repo = like_repo
        self.favorite_repo = favorite_repo
        self.comment_repo = comment_repo

    async def create_recipe(
        self, data: RecipeCreate, author_id: uuid.UUID
    ) -> RecipeRead:
        recipe = await self.repository.create(
            Recipe(
                author_id=author_id,
                title=data.title,
                description=data.description,
                visibility=data.visibility,
                cooking_time_minutes=data.cooking_time_minutes,
                servings=data.servings,
                difficulty=data.difficulty,
                category_id=data.category_id,
            )
        )
        return RecipeRead.model_validate(recipe)

    async def get_recipe(
        self, recipe_id: uuid.UUID, current_user_id: uuid.UUID | None
    ) -> RecipeRead:
        recipe = await self.repository.get_by_id(recipe_id)
        if not recipe or recipe.status == RecipeStatus.deleted:
            raise HTTPException(status_code=404, detail="Recipe not found")
        if not self._can_view(recipe, current_user_id):
            raise HTTPException(status_code=404, detail="Recipe not found")
        recipe_read = RecipeRead.model_validate(recipe)
        return await self._enrich_single(recipe_read, current_user_id)

    async def list_recipes(
        self,
        current_user_id: uuid.UUID | None,
        category_id: uuid.UUID | None = None,
        author_id: uuid.UUID | None = None,
    ) -> list[RecipeRead]:
        recipes = await self.repository.list_visible(
            current_user_id, category_id, author_id
        )
        recipe_reads = [RecipeRead.model_validate(r) for r in recipes]
        return await self._enrich_batch(recipe_reads, current_user_id)

    async def update_recipe(
        self, recipe_id: uuid.UUID, data: RecipeUpdate, current_user_id: uuid.UUID
    ) -> RecipeRead:
        recipe = await self._get_owned(recipe_id, current_user_id)
        updates = data.model_dump(exclude_unset=True)
        recipe = await self.repository.update(recipe, updates)
        recipe_read = RecipeRead.model_validate(recipe)
        return await self._enrich_single(recipe_read, current_user_id)

    async def delete_recipe(
        self, recipe_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> None:
        recipe = await self._get_owned(recipe_id, current_user_id)
        await self.repository.delete(recipe)

    def _can_view(self, recipe: Recipe, current_user_id: uuid.UUID | None) -> bool:
        if current_user_id and recipe.author_id == current_user_id:
            return True
        return (
            recipe.status == RecipeStatus.published
            and recipe.visibility == RecipeVisibility.public
        )

    async def _get_owned(
        self, recipe_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> Recipe:
        recipe = await self.repository.get_by_id(recipe_id)
        if not recipe or recipe.status == RecipeStatus.deleted:
            raise HTTPException(status_code=404, detail="Recipe not found")
        if recipe.author_id != current_user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        return recipe

    async def _enrich_single(
        self, recipe_read: RecipeRead, user_id: uuid.UUID | None
    ) -> RecipeRead:
        updates: dict[str, object] = {}
        if self.like_repo:
            updates["likes_count"] = await self.like_repo.count(recipe_read.id)
            if user_id:
                updates["is_liked"] = (
                    await self.like_repo.get(user_id, recipe_read.id) is not None
                )
        if self.favorite_repo and user_id:
            updates["is_favorited"] = (
                await self.favorite_repo.get(user_id, recipe_read.id) is not None
            )
        if self.comment_repo:
            counts = await self.comment_repo.count_by_recipe_batch([recipe_read.id])
            updates["comment_count"] = counts.get(recipe_read.id, 0)
        return recipe_read.model_copy(update=updates) if updates else recipe_read

    async def _enrich_batch(
        self, recipe_reads: list[RecipeRead], user_id: uuid.UUID | None
    ) -> list[RecipeRead]:
        if not recipe_reads:
            return recipe_reads
        ids = [r.id for r in recipe_reads]
        count_map: dict[uuid.UUID, int] = {}
        liked_set: set[uuid.UUID] = set()
        favorited_set: set[uuid.UUID] = set()
        comment_count_map: dict[uuid.UUID, int] = {}
        if self.like_repo:
            count_map = await self.like_repo.count_batch(ids)
            if user_id:
                liked_set = await self.like_repo.user_liked_batch(user_id, ids)
        if self.favorite_repo and user_id:
            favorited_set = await self.favorite_repo.user_favorited_batch(user_id, ids)
        if self.comment_repo:
            comment_count_map = await self.comment_repo.count_by_recipe_batch(ids)
        return [
            r.model_copy(
                update={
                    "likes_count": count_map.get(r.id, 0),
                    "is_liked": r.id in liked_set,
                    "is_favorited": r.id in favorited_set,
                    "comment_count": comment_count_map.get(r.id, 0),
                }
            )
            for r in recipe_reads
        ]
