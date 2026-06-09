import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import (
    get_current_admin,
    get_current_moderator,
    get_current_superadmin,
    get_current_user,
)
from app.db.session import get_db
from app.models.user import User
from app.repositories.comment import CommentRepository
from app.repositories.moderation_action import ModerationActionRepository
from app.repositories.recipe import RecipeRepository
from app.repositories.report import ReportRepository
from app.repositories.user import UserRepository
from app.schemas.admin import (
    AdminCommentPage,
    AdminCommentRead,
    AdminRecipePage,
    AdminRecipeRead,
    AdminUserPage,
    AssignRoleRequest,
    BlockRequest,
    HideRequest,
    ReportCreate,
    ReportPage,
    ReportRead,
)
from app.schemas.user import UserRead
from app.services.admin import AdminService

router = APIRouter(prefix="/api/admin", tags=["admin"])


def _service(session: AsyncSession = Depends(get_db)) -> AdminService:
    return AdminService(
        UserRepository(session),
        RecipeRepository(session),
        CommentRepository(session),
        ReportRepository(session),
        ModerationActionRepository(session),
    )


# ── users ─────────────────────────────────────────────────────────────────────


@router.get("/users", response_model=AdminUserPage)
async def list_users(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None),
    role: str | None = Query(None),
    service: AdminService = Depends(_service),
    _: User = Depends(get_current_admin),
) -> AdminUserPage:
    return await service.list_users(page, size, search=search, role=role)


@router.post("/users/{user_id}/role", response_model=UserRead)
async def assign_role(
    user_id: uuid.UUID,
    data: AssignRoleRequest,
    service: AdminService = Depends(_service),
    actor: User = Depends(get_current_admin),
) -> UserRead:
    return await service.assign_role(user_id, data.role, actor)


@router.post("/users/{user_id}/block", response_model=UserRead)
async def block_user(
    user_id: uuid.UUID,
    data: BlockRequest,
    service: AdminService = Depends(_service),
    actor: User = Depends(get_current_superadmin),
) -> UserRead:
    return await service.block_user(user_id, actor, data.reason)


@router.post("/users/{user_id}/unblock", response_model=UserRead)
async def unblock_user(
    user_id: uuid.UUID,
    service: AdminService = Depends(_service),
    actor: User = Depends(get_current_superadmin),
) -> UserRead:
    return await service.unblock_user(user_id, actor)


# ── reports ───────────────────────────────────────────────────────────────────


@router.post("/reports", response_model=ReportRead, status_code=201)
async def create_report(
    data: ReportCreate,
    service: AdminService = Depends(_service),
    current_user: User = Depends(get_current_user),
) -> ReportRead:
    return await service.create_report(data, current_user.id)


@router.get("/reports", response_model=ReportPage)
async def list_reports(
    status: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    service: AdminService = Depends(_service),
    _: User = Depends(get_current_moderator),
) -> ReportPage:
    return await service.list_reports(status, page, size)


@router.post("/reports/{report_id}/review", response_model=ReportRead)
async def review_report(
    report_id: uuid.UUID,
    service: AdminService = Depends(_service),
    actor: User = Depends(get_current_moderator),
) -> ReportRead:
    return await service.review_report(report_id, actor)


@router.post("/reports/{report_id}/dismiss", response_model=ReportRead)
async def dismiss_report(
    report_id: uuid.UUID,
    service: AdminService = Depends(_service),
    actor: User = Depends(get_current_moderator),
) -> ReportRead:
    return await service.dismiss_report(report_id, actor)


# ── recipes ───────────────────────────────────────────────────────────────────


@router.get("/recipes", response_model=AdminRecipePage)
async def list_recipes_admin(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: str | None = Query(None),
    has_comments: bool = Query(False),
    service: AdminService = Depends(_service),
    _: User = Depends(get_current_moderator),
) -> AdminRecipePage:
    return await service.list_recipes_admin(
        page, size, search=search, has_comments=has_comments
    )


@router.post("/recipes/{recipe_id}/hide", response_model=AdminRecipeRead)
async def hide_recipe(
    recipe_id: uuid.UUID,
    data: HideRequest,
    service: AdminService = Depends(_service),
    actor: User = Depends(get_current_moderator),
) -> AdminRecipeRead:
    return await service.hide_recipe(recipe_id, actor, data.reason)


@router.post("/recipes/{recipe_id}/unhide", response_model=AdminRecipeRead)
async def unhide_recipe(
    recipe_id: uuid.UUID,
    service: AdminService = Depends(_service),
    actor: User = Depends(get_current_moderator),
) -> AdminRecipeRead:
    return await service.unhide_recipe(recipe_id, actor)


# ── comments ──────────────────────────────────────────────────────────────────


@router.get("/comments", response_model=AdminCommentPage)
async def list_comments_admin(
    page: int = Query(1, ge=1),
    size: int = Query(100, ge=1, le=100),
    recipe_id: uuid.UUID | None = Query(None),
    search: str | None = Query(None),
    status: str | None = Query(None),
    service: AdminService = Depends(_service),
    _: User = Depends(get_current_moderator),
) -> AdminCommentPage:
    return await service.list_comments_admin(
        page, size, recipe_id=recipe_id, search=search, status=status
    )


@router.post("/comments/{comment_id}/delete", response_model=AdminCommentRead)
async def delete_comment_admin(
    comment_id: uuid.UUID,
    service: AdminService = Depends(_service),
    actor: User = Depends(get_current_moderator),
) -> AdminCommentRead:
    return await service.delete_comment_admin(comment_id, actor)
