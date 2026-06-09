import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.report import ReportReason, ReportTargetType
from app.models.user import UserRole


class ReportCreate(BaseModel):
    target_type: ReportTargetType
    target_id: uuid.UUID
    reason: ReportReason
    description: str | None = None


class ReportRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    reporter_id: uuid.UUID
    target_type: str
    target_id: uuid.UUID
    reason: str
    description: str | None
    status: str
    reviewed_by: uuid.UUID | None
    reviewed_at: datetime | None
    created_at: datetime
    updated_at: datetime


class ReportPage(BaseModel):
    items: list[ReportRead]
    total: int
    page: int
    size: int
    has_more: bool


class AdminUserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str
    username: str
    role: str
    is_active: bool
    is_email_verified: bool
    avatar_url: str | None
    created_at: datetime


class AdminUserPage(BaseModel):
    items: list[AdminUserRead]
    total: int
    page: int
    size: int
    has_more: bool


class AssignRoleRequest(BaseModel):
    role: UserRole


class BlockRequest(BaseModel):
    reason: str | None = None


class AdminRecipeRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: str
    author_id: uuid.UUID
    status: str
    visibility: str
    is_hidden: bool
    created_at: datetime


class AdminRecipePage(BaseModel):
    items: list[AdminRecipeRead]
    total: int
    page: int
    size: int
    has_more: bool


class AdminCommentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    recipe_id: uuid.UUID
    author_id: uuid.UUID
    body: str
    is_hidden: bool
    is_deleted: bool
    created_at: datetime


class AdminCommentPage(BaseModel):
    items: list[AdminCommentRead]
    total: int
    page: int
    size: int
    has_more: bool


class ModerationActionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    moderator_id: uuid.UUID
    action_type: str
    target_type: str
    target_id: uuid.UUID
    reason: str | None
    meta: dict | None
    created_at: datetime


class AuditPage(BaseModel):
    items: list[ModerationActionRead]
    total: int
    page: int
    size: int
    has_more: bool


class HideRequest(BaseModel):
    reason: str | None = None
