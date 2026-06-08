import uuid

from celery.result import AsyncResult
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.celery_app import celery_app
from app.db.session import get_db
from app.models.user import User
from app.repositories.shopping_list import ShoppingListRepository
from app.schemas.shopping_list import (
    GenerateRequest,
    GenerateTaskResponse,
    ShoppingListItemCreate,
    ShoppingListItemRead,
    ShoppingListItemUpdate,
    ShoppingListRead,
    TaskStatusResponse,
)
from app.services.shopping_list import ShoppingListService
from app.tasks.shopping_list import generate_shopping_list_task

router = APIRouter(prefix="/api/shopping-list", tags=["shopping-list"])


def _service(session: AsyncSession = Depends(get_db)) -> ShoppingListService:
    return ShoppingListService(ShoppingListRepository(session))


@router.get("", response_model=ShoppingListRead)
async def get_shopping_list(
    service: ShoppingListService = Depends(_service),
    current_user: User = Depends(get_current_user),
) -> ShoppingListRead:
    return await service.get_list(current_user.id)


@router.post("/generate", response_model=GenerateTaskResponse, status_code=202)
async def generate_shopping_list(
    data: GenerateRequest,
    current_user: User = Depends(get_current_user),
) -> GenerateTaskResponse:
    dates = [str(d) for d in data.dates] if data.dates else None
    task = generate_shopping_list_task.delay(str(current_user.id), data.mode, dates)
    return GenerateTaskResponse(task_id=task.id)


@router.get("/generate/status/{task_id}", response_model=TaskStatusResponse)
async def get_generate_status(
    task_id: str,
    current_user: User = Depends(get_current_user),
) -> TaskStatusResponse:
    result = AsyncResult(task_id, app=celery_app)
    if result.state == "SUCCESS":
        return TaskStatusResponse(status="success")
    if result.state == "FAILURE":
        return TaskStatusResponse(status="failure", error=str(result.result))
    if result.state == "STARTED":
        return TaskStatusResponse(status="started")
    return TaskStatusResponse(status="pending")


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
