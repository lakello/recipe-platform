import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin, get_optional_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.ingredient_category import IngredientCategoryRepository
from app.schemas.ingredient_category import (
    IngredientCategoryCreate,
    IngredientCategoryRead,
    IngredientCategoryUpdate,
)
from app.services.ingredient_category import IngredientCategoryService

router = APIRouter(prefix="/api/ingredient-categories", tags=["ingredient-categories"])


def _service(session: AsyncSession = Depends(get_db)) -> IngredientCategoryService:
    return IngredientCategoryService(IngredientCategoryRepository(session))


@router.get("", response_model=list[IngredientCategoryRead])
async def list_ingredient_categories(
    service: IngredientCategoryService = Depends(_service),
    _: User | None = Depends(get_optional_user),
) -> list[IngredientCategoryRead]:
    return await service.list_categories()


@router.post("", response_model=IngredientCategoryRead, status_code=201)
async def create_ingredient_category(
    data: IngredientCategoryCreate,
    service: IngredientCategoryService = Depends(_service),
    _: User = Depends(get_current_admin),
) -> IngredientCategoryRead:
    return await service.create_category(data)


@router.patch("/{category_id}", response_model=IngredientCategoryRead)
async def update_ingredient_category(
    category_id: uuid.UUID,
    data: IngredientCategoryUpdate,
    service: IngredientCategoryService = Depends(_service),
    _: User = Depends(get_current_admin),
) -> IngredientCategoryRead:
    return await service.update_category(category_id, data)


@router.delete("/{category_id}", status_code=204)
async def delete_ingredient_category(
    category_id: uuid.UUID,
    service: IngredientCategoryService = Depends(_service),
    _: User = Depends(get_current_admin),
) -> None:
    await service.delete_category(category_id)
