import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class RecipeStatus(enum.StrEnum):
    draft = "draft"
    published = "published"
    deleted = "deleted"


class RecipeVisibility(enum.StrEnum):
    public = "public"
    private = "private"


class Difficulty(enum.StrEnum):
    easy = "easy"
    medium = "medium"
    hard = "hard"


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    author_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str | None] = mapped_column(Text)
    status: Mapped[RecipeStatus] = mapped_column(
        Enum(RecipeStatus), default=RecipeStatus.draft
    )
    visibility: Mapped[RecipeVisibility] = mapped_column(
        Enum(RecipeVisibility), default=RecipeVisibility.public
    )
    cooking_time_minutes: Mapped[int | None] = mapped_column(Integer)
    servings: Mapped[int | None] = mapped_column(Integer)
    difficulty: Mapped[Difficulty | None] = mapped_column(Enum(Difficulty))
    category_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    category: Mapped["Category | None"] = relationship("Category", lazy="selectin")  # noqa: F821
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
