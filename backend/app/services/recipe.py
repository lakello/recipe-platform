import uuid

from fastapi import HTTPException

from app.models.recipe import Recipe, RecipeStatus, RecipeVisibility
from app.repositories.recipe import RecipeRepository
from app.schemas.recipe import RecipeCreate, RecipeRead, RecipeUpdate


class RecipeService:
    def __init__(self, repository: RecipeRepository) -> None:
        self.repository = repository

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
        return RecipeRead.model_validate(recipe)

    async def list_recipes(
        self, current_user_id: uuid.UUID | None
    ) -> list[RecipeRead]:
        recipes = await self.repository.list_visible(current_user_id)
        return [RecipeRead.model_validate(r) for r in recipes]

    async def update_recipe(
        self, recipe_id: uuid.UUID, data: RecipeUpdate, current_user_id: uuid.UUID
    ) -> RecipeRead:
        recipe = await self._get_owned(recipe_id, current_user_id)
        updates = data.model_dump(exclude_unset=True)
        recipe = await self.repository.update(recipe, updates)
        return RecipeRead.model_validate(recipe)

    async def delete_recipe(
        self, recipe_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> None:
        recipe = await self._get_owned(recipe_id, current_user_id)
        await self.repository.delete(recipe)

    def _can_view(
        self, recipe: Recipe, current_user_id: uuid.UUID | None
    ) -> bool:
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
