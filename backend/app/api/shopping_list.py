import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.shopping_list import ShoppingListRepository
from app.schemas.shopping_list import (
    GenerateRequest,
    ShoppingListItemCreate,
    ShoppingListItemRead,
    ShoppingListItemUpdate,
    ShoppingListRead,
)
from app.services.shopping_list import ShoppingListService

router = APIRouter(prefix="/api/shopping-list", tags=["shopping-list"])


def _service(session: AsyncSession = Depends(get_db)) -> ShoppingListService:
    return ShoppingListService(ShoppingListRepository(session))


@router.get("", response_model=ShoppingListRead)
async def get_shopping_list(
    service: ShoppingListService = Depends(_service),
    current_user: User = Depends(get_current_user),
) -> ShoppingListRead:
    return await service.get_list(current_user.id)


@router.post("/generate", response_model=ShoppingListRead)
async def generate_shopping_list(
    data: GenerateRequest,
    service: ShoppingListService = Depends(_service),
    current_user: User = Depends(get_current_user),
) -> ShoppingListRead:
    return await service.generate(current_user.id, data)


@router.post("/items", response_model=ShoppingListItemRead, status_code=201)
async def add_item(
    data: ShoppingListItemCreate,
    service: ShoppingListService = Depends(_service),
    current_user: User = Depends(get_current_user),
) -> ShoppingListItemRead:
    return await service.add_item(current_user.id, data)


@router.patch("/items/{item_id}", response_model=ShoppingListItemRead)
async def update_item(
    item_id: uuid.UUID,
    data: ShoppingListItemUpdate,
    service: ShoppingListService = Depends(_service),
    current_user: User = Depends(get_current_user),
) -> ShoppingListItemRead:
    return await service.update_item(current_user.id, item_id, data)


@router.delete("/items/{item_id}", status_code=204)
async def delete_item(
    item_id: uuid.UUID,
    service: ShoppingListService = Depends(_service),
    current_user: User = Depends(get_current_user),
) -> None:
    await service.delete_item(current_user.id, item_id)
