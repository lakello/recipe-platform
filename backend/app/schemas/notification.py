import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from app.models.notification import Notification


class NotificationRead(BaseModel):
    id: uuid.UUID
    type: str
    actor_id: uuid.UUID | None
    actor_username: str | None
    actor_avatar_url: str | None
    entity_id: uuid.UUID | None
    entity_type: str | None
    body: str | None
    is_read: bool
    created_at: datetime

    @classmethod
    def from_orm(cls, n: "Notification") -> "NotificationRead":
        return cls(
            id=n.id,
            type=n.type,
            actor_id=n.actor_id,
            actor_username=n.actor.username if n.actor else None,
            actor_avatar_url=n.actor.avatar_url if n.actor else None,
            entity_id=n.entity_id,
            entity_type=n.entity_type,
            body=n.body,
            is_read=n.is_read,
            created_at=n.created_at,
        )


class NotificationPage(BaseModel):
    items: list[NotificationRead]
    total: int
    page: int
    size: int
    has_more: bool
    unread_count: int


class UnreadCount(BaseModel):
    count: int
