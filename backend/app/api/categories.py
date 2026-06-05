import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin, get_optional_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.category import CategoryRepository
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.services.category import CategoryService

router = APIRouter(prefix="/api/categories", tags=["categories"])


def _category_service(session: AsyncSession = Depends(get_db)) -> CategoryService:
    return CategoryService(CategoryRepository(session))


@router.get("", response_model=list[CategoryRead])
async def list_categories(
    service: CategoryService = Depends(_category_service),
    _: User | None = Depends(get_optional_user),
) -> list[CategoryRead]:
    return await service.list_categories()


@router.get("/{category_id}", response_model=CategoryRead)
async def get_category(
    category_id: uuid.UUID,
    service: CategoryService = Depends(_category_service),
) -> CategoryRead:
    return await service.get_category(category_id)


@router.post("", response_model=CategoryRead, status_code=201)
async def create_category(
    data: CategoryCreate,
    service: CategoryService = Depends(_category_service),
    _: User = Depends(get_current_admin),
) -> CategoryRead:
    return await service.create_category(data)


@router.patch("/{category_id}", response_model=CategoryRead)
async def update_category(
    category_id: uuid.UUID,
    data: CategoryUpdate,
    service: CategoryService = Depends(_category_service),
    _: User = Depends(get_current_admin),
) -> CategoryRead:
    return await service.update_category(category_id, data)


@router.delete("/{category_id}", status_code=204)
async def delete_category(
    category_id: uuid.UUID,
    service: CategoryService = Depends(_category_service),
    _: User = Depends(get_current_admin),
) -> None:
    await service.delete_category(category_id)
