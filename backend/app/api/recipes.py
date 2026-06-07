import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_optional_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.comment import CommentRepository
from app.repositories.like import FavoriteRepository, LikeRepository
from app.repositories.recipe import RecipeRepository
from app.schemas.recipe import RecipeCreate, RecipeRead, RecipeUpdate
from app.services.recipe import RecipeService

router = APIRouter(prefix="/api/recipes", tags=["recipes"])


def _recipe_service(session: AsyncSession = Depends(get_db)) -> RecipeService:
    return RecipeService(
        RecipeRepository(session),
        LikeRepository(session),
        FavoriteRepository(session),
        CommentRepository(session),
    )


@router.post("", response_model=RecipeRead, status_code=201)
async def create_recipe(
    data: RecipeCreate,
    service: RecipeService = Depends(_recipe_service),
    current_user: User = Depends(get_current_user),
) -> RecipeRead:
    return await service.create_recipe(data, current_user.id)


@router.get("", response_model=list[RecipeRead])
async def list_recipes(
    category_id: uuid.UUID | None = Query(None),
    author_id: uuid.UUID | None = Query(None),
    service: RecipeService = Depends(_recipe_service),
    current_user: User | None = Depends(get_optional_user),
) -> list[RecipeRead]:
    user_id = current_user.id if current_user else None
    return await service.list_recipes(user_id, category_id, author_id)


@router.get("/{recipe_id}", response_model=RecipeRead)
async def get_recipe(
    recipe_id: uuid.UUID,
    service: RecipeService = Depends(_recipe_service),
    current_user: User | None = Depends(get_optional_user),
) -> RecipeRead:
    user_id = current_user.id if current_user else None
    return await service.get_recipe(recipe_id, user_id)


@router.patch("/{recipe_id}", response_model=RecipeRead)
async def update_recipe(
    recipe_id: uuid.UUID,
    data: RecipeUpdate,
    service: RecipeService = Depends(_recipe_service),
    current_user: User = Depends(get_current_user),
) -> RecipeRead:
    return await service.update_recipe(recipe_id, data, current_user.id)


@router.delete("/{recipe_id}", status_code=204)
async def delete_recipe(
    recipe_id: uuid.UUID,
    service: RecipeService = Depends(_recipe_service),
    current_user: User = Depends(get_current_user),
) -> None:
    await service.delete_recipe(recipe_id, current_user.id)
