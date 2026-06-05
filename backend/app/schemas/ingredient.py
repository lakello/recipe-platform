import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.ingredient import IngredientUnit


class IngredientRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    created_at: datetime


class RecipeIngredientItem(BaseModel):
    ingredient_name: str = Field(min_length=1, max_length=255)
    amount: float | None = Field(None, gt=0)
    unit: IngredientUnit | None = None


class RecipeIngredientRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    ingredient_id: uuid.UUID
    ingredient: IngredientRead
    amount: float | None
    unit: IngredientUnit | None
    order: int


class RecipeStepItem(BaseModel):
    title: str | None = Field(None, max_length=255)
    description: str = Field(min_length=1)


class RecipeStepRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    order: int
    title: str | None
    description: str
