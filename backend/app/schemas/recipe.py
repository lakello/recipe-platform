import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.recipe import Difficulty, RecipeStatus, RecipeVisibility
from app.schemas.category import CategoryRead
from app.schemas.ingredient import RecipeIngredientRead, RecipeStepRead


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
    title: str
    description: str | None
    status: RecipeStatus
    visibility: RecipeVisibility
    cooking_time_minutes: int | None
    servings: int | None
    difficulty: Difficulty | None
    category_id: uuid.UUID | None
    category: CategoryRead | None
    ingredients: list[RecipeIngredientRead]
    steps: list[RecipeStepRead]
    created_at: datetime
    updated_at: datetime
