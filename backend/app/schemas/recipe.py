import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.recipe import Difficulty, RecipeStatus, RecipeVisibility
from app.schemas.category import CategoryRead
from app.schemas.ingredient import RecipeIngredientRead, RecipeStepRead
from app.schemas.upload import RecipePhotoRead


class RecipeAuthorRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    username: str
    avatar_url: str | None


class RecipeCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = None
    visibility: RecipeVisibility = RecipeVisibility.public
    cooking_time_minutes: int | None = Field(None, gt=0)
    servings: int | None = Field(None, gt=0)
    difficulty: Difficulty | None = None
    category_id: uuid.UUID | None = None


class RecipeUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None
    status: RecipeStatus | None = None
    visibility: RecipeVisibility | None = None
    cooking_time_minutes: int | None = Field(None, gt=0)
    servings: int | None = Field(None, gt=0)
    difficulty: Difficulty | None = None
    category_id: uuid.UUID | None = None


class RecipeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    author_id: uuid.UUID
    author: RecipeAuthorRead
    title: str
    description: str | None
    status: RecipeStatus
    visibility: RecipeVisibility
    cooking_time_minutes: int | None
    servings: int | None
    difficulty: Difficulty | None
    category_id: uuid.UUID | None
    category: CategoryRead | None
    photo: RecipePhotoRead | None
    ingredients: list[RecipeIngredientRead]
    steps: list[RecipeStepRead]
    likes_count: int = 0
    is_liked: bool = False
    is_favorited: bool = False
    comment_count: int = 0
    created_at: datetime
    updated_at: datetime
