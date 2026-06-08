import uuid
from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.ingredient import IngredientRead


class ShoppingListItemCreate(BaseModel):
    ingredient_id: uuid.UUID | None = None
    name: str = Field(min_length=1, max_length=255)
    amount: float | None = Field(None, gt=0)
    unit: str | None = None


class ShoppingListItemUpdate(BaseModel):
    is_bought: bool | None = None
    amount: float | None = Field(None, gt=0)
    unit: str | None = None


class ShoppingListItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    ingredient_id: uuid.UUID | None
    ingredient: IngredientRead | None
    name: str
    amount: float | None
    unit: str | None
    is_bought: bool
    is_manual: bool
    created_at: datetime


class ShoppingListRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    last_generated_at: datetime | None
    items: list[ShoppingListItemRead]


class GenerateRequest(BaseModel):
    mode: Literal["today", "week", "custom"]
    dates: list[date] | None = None


class GenerateTaskResponse(BaseModel):
    task_id: str


class TaskStatusResponse(BaseModel):
    status: Literal["pending", "started", "success", "failure"]
    error: str | None = None
