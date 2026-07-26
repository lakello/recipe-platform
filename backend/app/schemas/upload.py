import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class PresignRequest(BaseModel):
    upload_type: Literal["recipe_photo", "avatar"]
    content_type: Literal["image/jpeg", "image/png", "image/webp"]
    recipe_id: uuid.UUID | None = None


class PresignResponse(BaseModel):
    upload_id: uuid.UUID
    upload_url: str
    fields: dict[str, str]
    key: str


class AttachPhotoRequest(BaseModel):
    upload_id: uuid.UUID


class UploadStatusRead(BaseModel):
    upload_id: uuid.UUID
    status: Literal["pending", "validating", "validated", "failed", "attached"]


class RecipePhotoRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    key: str
    content_type: str
    created_at: datetime
