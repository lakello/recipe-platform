import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_moderator, get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.comment import CommentRepository
from app.repositories.recipe import RecipeRepository
from app.schemas.comment import CommentCreate, CommentPage, CommentRead, CommentUpdate
from app.services.comment import CommentService

router = APIRouter(tags=["comments"])


def _service(session: AsyncSession = Depends(get_db)) -> CommentService:
    return CommentService(CommentRepository(session), RecipeRepository(session))


@router.post(
    "/api/recipes/{recipe_id}/comments",
    response_model=CommentRead,
    status_code=201,
)
async def add_comment(
    recipe_id: uuid.UUID,
    data: CommentCreate,
    service: CommentService = Depends(_service),
    current_user: User = Depends(get_current_user),
) -> CommentRead:
    return await service.add_comment(recipe_id, current_user.id, data)


@router.get("/api/recipes/{recipe_id}/comments", response_model=CommentPage)
async def list_comments(
    recipe_id: uuid.UUID,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=50),
    service: CommentService = Depends(_service),
) -> CommentPage:
    return await service.list_comments(recipe_id, page, size)


@router.get("/api/comments/{comment_id}/replies", response_model=CommentPage)
async def list_replies(
    comment_id: uuid.UUID,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=50),
    service: CommentService = Depends(_service),
) -> CommentPage:
    return await service.list_replies(comment_id, page, size)


@router.patch("/api/comments/{comment_id}", response_model=CommentRead)
async def edit_comment(
    comment_id: uuid.UUID,
    data: CommentUpdate,
    service: CommentService = Depends(_service),
    current_user: User = Depends(get_current_user),
) -> CommentRead:
    return await service.edit_comment(comment_id, current_user.id, data)


@router.delete("/api/comments/{comment_id}", status_code=204)
async def delete_comment(
    comment_id: uuid.UUID,
    service: CommentService = Depends(_service),
    current_user: User = Depends(get_current_user),
) -> None:
    await service.delete_comment(comment_id, current_user.id)


@router.post("/api/comments/{comment_id}/hide", response_model=CommentRead)
async def hide_comment(
    comment_id: uuid.UUID,
    service: CommentService = Depends(_service),
    _: User = Depends(get_current_moderator),
) -> CommentRead:
    return await service.hide_comment(comment_id)


@router.post("/api/comments/{comment_id}/unhide", response_model=CommentRead)
async def unhide_comment(
    comment_id: uuid.UUID,
    service: CommentService = Depends(_service),
    _: User = Depends(get_current_moderator),
) -> CommentRead:
    return await service.unhide_comment(comment_id)
