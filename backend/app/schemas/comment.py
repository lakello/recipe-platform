import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator


class CommentAuthor(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    role: str
    avatar_url: str | None


class CommentCreate(BaseModel):
    body: str = Field(min_length=1, max_length=2000)
    parent_id: uuid.UUID | None = None


class CommentUpdate(BaseModel):
    body: str = Field(min_length=1, max_length=2000)


class CommentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    recipe_id: uuid.UUID
    author_id: uuid.UUID
    parent_id: uuid.UUID | None
    body: str
    is_hidden: bool
    is_deleted: bool
    author: CommentAuthor
    reply_count: int = 0
    created_at: datetime
    updated_at: datetime

    @model_validator(mode="after")
    def mask_body(self) -> "CommentRead":
        if self.is_deleted:
            self.body = "Комментарий удалён"
        elif self.is_hidden:
            self.body = "Комментарий скрыт модератором"
        return self


class CommentPage(BaseModel):
    items: list[CommentRead]
    total: int
    page: int
    size: int
    has_more: bool
