import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.comment import CommentRepository
from app.repositories.notification import NotificationRepository
from app.repositories.notification_preferences import NotificationPreferencesRepository
from app.repositories.recipe import RecipeRepository
from app.schemas.notification import (
    NotificationPage,
    NotificationPreferencesRead,
    NotificationPreferencesUpdate,
    NotificationRead,
    UnreadCount,
)
from app.services.notification import NotificationService

router = APIRouter(tags=["notifications"])


def _service(session: AsyncSession = Depends(get_db)) -> NotificationService:
    return NotificationService(
        NotificationRepository(session),
        RecipeRepository(session),
        CommentRepository(session),
    )


def _prefs_repo(
    session: AsyncSession = Depends(get_db),
) -> NotificationPreferencesRepository:
    return NotificationPreferencesRepository(session)


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


@router.get(
    "/api/notifications/preferences", response_model=NotificationPreferencesRead
)
async def get_preferences(
    repo: NotificationPreferencesRepository = Depends(_prefs_repo),
    current_user: User = Depends(get_current_user),
) -> NotificationPreferencesRead:
    prefs = await repo.get_or_default(current_user.id)
    return NotificationPreferencesRead(
        email_like=prefs.email_like,
        email_comment=prefs.email_comment,
        email_follow=prefs.email_follow,
    )


@router.patch(
    "/api/notifications/preferences", response_model=NotificationPreferencesRead
)
async def update_preferences(
    body: NotificationPreferencesUpdate,
    repo: NotificationPreferencesRepository = Depends(_prefs_repo),
    current_user: User = Depends(get_current_user),
) -> NotificationPreferencesRead:
    updates = body.model_dump(exclude_none=True)
    prefs = await repo.update(current_user.id, updates)
    return NotificationPreferencesRead(
        email_like=prefs.email_like,
        email_comment=prefs.email_comment,
        email_follow=prefs.email_follow,
    )
