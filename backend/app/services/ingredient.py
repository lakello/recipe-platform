import uuid

from fastapi import HTTPException

from app.models.recipe import Recipe
from app.repositories.ingredient import IngredientRepository
from app.repositories.recipe import RecipeRepository
from app.schemas.ingredient import (
    IngredientRead,
    RecipeIngredientItem,
    RecipeStepItem,
)
from app.schemas.recipe import RecipeRead


class IngredientService:
    def __init__(
        self,
        ingredient_repo: IngredientRepository,
        recipe_repo: RecipeRepository,
    ) -> None:
        self.ingredient_repo = ingredient_repo
        self.recipe_repo = recipe_repo

    async def search_ingredients(self, query: str) -> list[IngredientRead]:
        results = await self.ingredient_repo.search(query)
        return [IngredientRead.model_validate(i) for i in results]

    async def set_ingredients(
        self,
        recipe_id: uuid.UUID,
        current_user_id: uuid.UUID,
        items: list[RecipeIngredientItem],
    ) -> RecipeRead:
        await self._get_owned(recipe_id, current_user_id)
        await self.ingredient_repo.replace_recipe_ingredients(
            recipe_id,
            [i.model_dump() for i in items],
        )
        # session.refresh() does not re-trigger selectin loading after commit;
        # re-query instead to get fresh relationships from the database.
        recipe = await self.recipe_repo.get_by_id(recipe_id)
        return RecipeRead.model_validate(recipe)

    async def set_steps(
        self,
        recipe_id: uuid.UUID,
        current_user_id: uuid.UUID,
        items: list[RecipeStepItem],
    ) -> RecipeRead:
        await self._get_owned(recipe_id, current_user_id)
        await self.ingredient_repo.replace_recipe_steps(
            recipe_id,
            [i.model_dump() for i in items],
        )
        recipe = await self.recipe_repo.get_by_id(recipe_id)
        return RecipeRead.model_validate(recipe)

    async def _get_owned(
        self, recipe_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> Recipe:
        recipe = await self.recipe_repo.get_by_id(recipe_id)
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")
        if recipe.author_id != current_user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        return recipe
