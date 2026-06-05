import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.ingredient import IngredientRepository
from app.repositories.recipe import RecipeRepository
from app.schemas.ingredient import (
    IngredientRead,
    RecipeIngredientItem,
    RecipeStepItem,
)
from app.schemas.recipe import RecipeRead
from app.services.ingredient import IngredientService

router = APIRouter(tags=["ingredients"])


def _ingredient_service(session: AsyncSession = Depends(get_db)) -> IngredientService:
    return IngredientService(
        IngredientRepository(session),
        RecipeRepository(session),
    )


@router.get("/api/ingredients", response_model=list[IngredientRead])
async def search_ingredients(
    search: str = Query("", min_length=0),
    service: IngredientService = Depends(_ingredient_service),
) -> list[IngredientRead]:
    return await service.search_ingredients(search)


@router.put("/api/recipes/{recipe_id}/ingredients", response_model=RecipeRead)
async def set_recipe_ingredients(
    recipe_id: uuid.UUID,
    items: list[RecipeIngredientItem],
    service: IngredientService = Depends(_ingredient_service),
    current_user: User = Depends(get_current_user),
) -> RecipeRead:
    return await service.set_ingredients(recipe_id, current_user.id, items)


@router.put("/api/recipes/{recipe_id}/steps", response_model=RecipeRead)
async def set_recipe_steps(
    recipe_id: uuid.UUID,
    items: list[RecipeStepItem],
    service: IngredientService = Depends(_ingredient_service),
    current_user: User = Depends(get_current_user),
) -> RecipeRead:
    return await service.set_steps(recipe_id, current_user.id, items)
