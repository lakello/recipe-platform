import uuid
from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from app.models.meal_plan import MealType
from app.models.recipe import Difficulty
from app.schemas.category import CategoryRead
from app.schemas.upload import RecipePhotoRead


class RecipeSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    cooking_time_minutes: int | None
    servings: int | None
    difficulty: Difficulty | None
    photo: RecipePhotoRead | None
    category: CategoryRead | None


class MealPlanItemCreate(BaseModel):
    week_start: date
    day_of_week: int = Field(ge=0, le=6)
    meal_type: MealType
    recipe_id: uuid.UUID
    servings: int = Field(1, ge=1)


class MealPlanItemUpdate(BaseModel):
    servings: int = Field(..., ge=1)


class MealPlanItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    day_of_week: int
    meal_type: MealType
    recipe_id: uuid.UUID
    recipe: RecipeSummary
    servings: int


class MealPlanRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    week_start: date
    items: list[MealPlanItemRead]


class CopyWeekRequest(BaseModel):
    week_start: date


class CopyFromWeekRequest(BaseModel):
    source_week_start: date
    target_week_start: date
