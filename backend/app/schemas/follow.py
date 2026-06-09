import uuid

from pydantic import BaseModel


class FollowUserRead(BaseModel):
    id: uuid.UUID
    username: str
    avatar_url: str | None
    is_following: bool = False


class FollowUserPage(BaseModel):
    items: list[FollowUserRead]
    total: int
    page: int
    size: int
    has_more: bool
