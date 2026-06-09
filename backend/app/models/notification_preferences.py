import uuid

from sqlalchemy import Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class NotificationPreferences(Base):
    __tablename__ = "notification_preferences"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    email_like: Mapped[bool] = mapped_column(Boolean, default=True, server_default="t")
    email_comment: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="t"
    )
    email_follow: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default="t"
    )
