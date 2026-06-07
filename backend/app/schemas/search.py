import uuid
from typing import Literal

from pydantic import BaseModel, Field

from app.models.recipe import Difficulty
from app.schemas.recipe import RecipeRead


class SearchParams(BaseModel):
    q: str | None = None
    category_id: uuid.UUID | None = None
    min_time: int | None = Field(None, gt=0)
    max_time: int | None = Field(None, gt=0)
    difficulty: Difficulty | None = None
    include_ingredients: list[str] = Field(default_factory=list)
    exclude_ingredients: list[str] = Field(default_factory=list)
    sort: Literal["relevance", "newest", "popular"] = "relevance"
    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1, le=100)


class SearchResult(BaseModel):
    total: int
    page: int
    size: int
    items: list[RecipeRead]
