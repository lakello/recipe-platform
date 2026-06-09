import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_optional_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.comment import CommentRepository
from app.repositories.like import FavoriteRepository, LikeRepository
from app.repositories.notification import NotificationRepository
from app.repositories.recipe import RecipeRepository
from app.schemas.like import FavoriteStatus, LikeStatus
from app.schemas.recipe import RecipeRead
from app.services.like import FavoriteService, LikeService
from app.services.notification import NotificationService

router = APIRouter(tags=["likes"])


def _like_service(session: AsyncSession = Depends(get_db)) -> LikeService:
    return LikeService(LikeRepository(session), RecipeRepository(session))


def _favorite_service(session: AsyncSession = Depends(get_db)) -> FavoriteService:
    return FavoriteService(
        FavoriteRepository(session),
        LikeRepository(session),
        RecipeRepository(session),
    )


def _notif_service(session: AsyncSession = Depends(get_db)) -> NotificationService:
    return NotificationService(
        NotificationRepository(session),
        RecipeRepository(session),
        CommentRepository(session),
    )


@router.post("/api/recipes/{recipe_id}/like", response_model=LikeStatus)
async def like_recipe(
    recipe_id: uuid.UUID,
    service: LikeService = Depends(_like_service),
    notif_service: NotificationService = Depends(_notif_service),
    current_user: User = Depends(get_current_user),
) -> LikeStatus:
    result = await service.like(recipe_id, current_user.id)
    notif = await notif_service.create_like_notification(current_user.id, recipe_id)
    if notif:
        from app.tasks.email import send_notification_email

        send_notification_email.delay(str(notif.id))
    return result


@router.delete("/api/recipes/{recipe_id}/like", response_model=LikeStatus)
async def unlike_recipe(
    recipe_id: uuid.UUID,
    service: LikeService = Depends(_like_service),
    current_user: User = Depends(get_current_user),
) -> LikeStatus:
    return await service.unlike(recipe_id, current_user.id)


@router.get("/api/recipes/{recipe_id}/like", response_model=LikeStatus)
async def get_like_status(
    recipe_id: uuid.UUID,
    service: LikeService = Depends(_like_service),
    current_user: User | None = Depends(get_optional_user),
) -> LikeStatus:
    user_id = current_user.id if current_user else None
    return await service.get_status(recipe_id, user_id)


@router.post("/api/recipes/{recipe_id}/favorite", response_model=FavoriteStatus)
async def add_favorite(
    recipe_id: uuid.UUID,
    service: FavoriteService = Depends(_favorite_service),
    current_user: User = Depends(get_current_user),
) -> FavoriteStatus:
    return await service.add_favorite(recipe_id, current_user.id)


@router.delete("/api/recipes/{recipe_id}/favorite", response_model=FavoriteStatus)
async def remove_favorite(
    recipe_id: uuid.UUID,
    service: FavoriteService = Depends(_favorite_service),
    current_user: User = Depends(get_current_user),
) -> FavoriteStatus:
    return await service.remove_favorite(recipe_id, current_user.id)


@router.get("/api/users/me/favorites", response_model=list[RecipeRead])
async def list_favorites(
    service: FavoriteService = Depends(_favorite_service),
    current_user: User = Depends(get_current_user),
) -> list[RecipeRead]:
    return await service.list_favorites(current_user.id)
