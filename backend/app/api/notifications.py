import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.comment import CommentRepository
from app.repositories.notification import NotificationRepository
from app.repositories.recipe import RecipeRepository
from app.schemas.notification import NotificationPage, NotificationRead, UnreadCount
from app.services.notification import NotificationService

router = APIRouter(tags=["notifications"])


def _service(session: AsyncSession = Depends(get_db)) -> NotificationService:
    return NotificationService(
        NotificationRepository(session),
        RecipeRepository(session),
        CommentRepository(session),
    )


@router.get("/api/notifications", response_model=NotificationPage)
async def list_notifications(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=50),
    service: NotificationService = Depends(_service),
    current_user: User = Depends(get_current_user),
) -> NotificationPage:
    return await service.list(current_user.id, page, size)


@router.get("/api/notifications/unread-count", response_model=UnreadCount)
async def get_unread_count(
    service: NotificationService = Depends(_service),
    current_user: User = Depends(get_current_user),
) -> UnreadCount:
    return await service.count_unread(current_user.id)


@router.patch("/api/notifications/read-all", status_code=204)
async def mark_all_read(
    service: NotificationService = Depends(_service),
    current_user: User = Depends(get_current_user),
) -> None:
    await service.mark_all_read(current_user.id)


@router.patch(
    "/api/notifications/{notification_id}/read", response_model=NotificationRead
)
async def mark_read(
    notification_id: uuid.UUID,
    service: NotificationService = Depends(_service),
    current_user: User = Depends(get_current_user),
) -> NotificationRead:
    return await service.mark_read(notification_id, current_user.id)
