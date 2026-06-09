import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_optional_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.comment import CommentRepository
from app.repositories.follow import FollowRepository
from app.repositories.like import FavoriteRepository, LikeRepository
from app.repositories.notification import NotificationRepository
from app.repositories.recipe import RecipeRepository
from app.repositories.user import UserRepository
from app.schemas.follow import FollowUserPage
from app.schemas.recipe import RecipeRead
from app.services.follow import FollowService
from app.services.notification import NotificationService
from app.services.recipe import RecipeService

router = APIRouter(tags=["follows"])


def _follow_service(session: AsyncSession = Depends(get_db)) -> FollowService:
    return FollowService(FollowRepository(session), UserRepository(session))


def _notif_service(session: AsyncSession = Depends(get_db)) -> NotificationService:
    return NotificationService(
        NotificationRepository(session),
        RecipeRepository(session),
        CommentRepository(session),
    )


def _recipe_service(session: AsyncSession = Depends(get_db)) -> RecipeService:
    return RecipeService(
        RecipeRepository(session),
        LikeRepository(session),
        FavoriteRepository(session),
        CommentRepository(session),
    )


@router.post("/api/users/{user_id}/follow", status_code=204)
async def follow_user(
    user_id: uuid.UUID,
    service: FollowService = Depends(_follow_service),
    notif_service: NotificationService = Depends(_notif_service),
    current_user: User = Depends(get_current_user),
) -> None:
    await service.follow(current_user.id, user_id)
    notif = await notif_service.create_follow_notification(current_user.id, user_id)
    from app.tasks.email import send_notification_email

    send_notification_email.delay(str(notif.id))


@router.delete("/api/users/{user_id}/follow", status_code=204)
async def unfollow_user(
    user_id: uuid.UUID,
    service: FollowService = Depends(_follow_service),
    current_user: User = Depends(get_current_user),
) -> None:
    await service.unfollow(current_user.id, user_id)


@router.get("/api/users/{user_id}/followers", response_model=FollowUserPage)
async def list_followers(
    user_id: uuid.UUID,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    service: FollowService = Depends(_follow_service),
    current_user: User | None = Depends(get_optional_user),
) -> FollowUserPage:
    return await service.list_followers(
        user_id,
        current_user.id if current_user else None,
        page,
        size,
    )


@router.get("/api/users/{user_id}/following", response_model=FollowUserPage)
async def list_following(
    user_id: uuid.UUID,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    service: FollowService = Depends(_follow_service),
    current_user: User | None = Depends(get_optional_user),
) -> FollowUserPage:
    return await service.list_following(
        user_id,
        current_user.id if current_user else None,
        page,
        size,
    )


@router.get("/api/feed", response_model=list[RecipeRead])
async def get_feed(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db),
    recipe_service: RecipeService = Depends(_recipe_service),
    current_user: User = Depends(get_current_user),
) -> list[RecipeRead]:
    follow_repo = FollowRepository(session)
    author_ids = await follow_repo.get_following_ids(current_user.id)
    recipes, _ = await RecipeRepository(session).list_feed(author_ids, page, size)
    recipe_reads = [RecipeRead.model_validate(r) for r in recipes]
    return await recipe_service._enrich_batch(recipe_reads, current_user.id)
