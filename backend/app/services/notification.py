import uuid

from fastapi import HTTPException

from app.models.notification import Notification, NotificationType
from app.repositories.comment import CommentRepository
from app.repositories.notification import NotificationRepository
from app.repositories.recipe import RecipeRepository
from app.schemas.notification import NotificationPage, NotificationRead, UnreadCount

_PAGE_SIZE_MAX = 50


class NotificationService:
    def __init__(
        self,
        notification_repo: NotificationRepository,
        recipe_repo: RecipeRepository,
        comment_repo: CommentRepository,
    ) -> None:
        self.notification_repo = notification_repo
        self.recipe_repo = recipe_repo
        self.comment_repo = comment_repo

    async def list(self, user_id: uuid.UUID, page: int, size: int) -> NotificationPage:
        size = min(size, _PAGE_SIZE_MAX)
        offset = (page - 1) * size
        notifications, total = await self.notification_repo.list_for_user(
            user_id, offset, size
        )
        unread = await self.notification_repo.count_unread(user_id)
        return NotificationPage(
            items=[NotificationRead.from_orm(n) for n in notifications],
            total=total,
            page=page,
            size=size,
            has_more=(offset + len(notifications)) < total,
            unread_count=unread,
        )

    async def mark_read(
        self, notification_id: uuid.UUID, user_id: uuid.UUID
    ) -> NotificationRead:
        n = await self.notification_repo.get_by_id(notification_id)
        if not n:
            raise HTTPException(status_code=404, detail="Notification not found")
        if n.user_id != user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        n = await self.notification_repo.mark_read(n)
        return NotificationRead.from_orm(n)

    async def mark_all_read(self, user_id: uuid.UUID) -> None:
        await self.notification_repo.mark_all_read(user_id)

    async def count_unread(self, user_id: uuid.UUID) -> UnreadCount:
        count = await self.notification_repo.count_unread(user_id)
        return UnreadCount(count=count)

    async def create_like_notification(
        self, liker_id: uuid.UUID, recipe_id: uuid.UUID
    ) -> Notification | None:
        recipe = await self.recipe_repo.get_by_id(recipe_id)
        if not recipe or recipe.author_id == liker_id:
            return None
        n = Notification(
            user_id=recipe.author_id,
            actor_id=liker_id,
            type=NotificationType.like,
            entity_id=recipe_id,
            entity_type="recipe",
        )
        return await self.notification_repo.create(n)

    async def create_comment_notification(
        self,
        author_id: uuid.UUID,
        recipe_id: uuid.UUID,
        comment_id: uuid.UUID,
        parent_id: uuid.UUID | None,
    ) -> Notification | None:
        if parent_id is not None:
            parent = await self.comment_repo.get_by_id(parent_id)
            if not parent or parent.author_id == author_id:
                return None
            n = Notification(
                user_id=parent.author_id,
                actor_id=author_id,
                type=NotificationType.reply,
                entity_id=recipe_id,
                entity_type="recipe",
            )
        else:
            recipe = await self.recipe_repo.get_by_id(recipe_id)
            if not recipe or recipe.author_id == author_id:
                return None
            n = Notification(
                user_id=recipe.author_id,
                actor_id=author_id,
                type=NotificationType.comment,
                entity_id=recipe_id,
                entity_type="recipe",
            )
        return await self.notification_repo.create(n)

    async def create_follow_notification(
        self, follower_id: uuid.UUID, following_id: uuid.UUID
    ) -> Notification:
        n = Notification(
            user_id=following_id,
            actor_id=follower_id,
            type=NotificationType.follow,
        )
        return await self.notification_repo.create(n)

    async def create_moderation_notification(
        self,
        user_id: uuid.UUID,
        body: str,
        entity_id: uuid.UUID | None = None,
        entity_type: str | None = None,
    ) -> Notification:
        n = Notification(
            user_id=user_id,
            actor_id=None,
            type=NotificationType.moderation,
            entity_id=entity_id,
            entity_type=entity_type,
            body=body,
        )
        return await self.notification_repo.create(n)
