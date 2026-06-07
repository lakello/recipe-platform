from pydantic import BaseModel


class LikeStatus(BaseModel):
    likes_count: int
    is_liked: bool


class FavoriteStatus(BaseModel):
    is_favorited: bool
