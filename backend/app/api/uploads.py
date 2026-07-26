import uuid

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.rate_limit import client_ip, enforce
from app.core.storage import presign_get
from app.db.session import get_db
from app.models.user import User
from app.repositories.photo import PhotoRepository
from app.repositories.recipe import RecipeRepository
from app.repositories.user import UserRepository
from app.schemas.recipe import RecipeRead
from app.schemas.upload import (
    AttachPhotoRequest,
    PresignRequest,
    PresignResponse,
    UploadStatusRead,
)
from app.schemas.user import UserRead
from app.services.upload import UploadService

router = APIRouter(prefix="/api/uploads", tags=["uploads"])


def _upload_service(session: AsyncSession = Depends(get_db)) -> UploadService:
    return UploadService(
        PhotoRepository(session),
        RecipeRepository(session),
        UserRepository(session),
    )


async def _limit_presign(request: Request) -> None:
    await enforce(request, "presign", client_ip(request), 30)


@router.post("/presign", response_model=PresignResponse)
async def presign(
    request: PresignRequest,
    _: None = Depends(_limit_presign),
    service: UploadService = Depends(_upload_service),
    current_user: User = Depends(get_current_user),
) -> PresignResponse:
    return await service.presign_upload(request, current_user.id)


@router.post("/recipes/{recipe_id}/photo", response_model=RecipeRead)
async def attach_recipe_photo(
    recipe_id: uuid.UUID,
    data: AttachPhotoRequest,
    service: UploadService = Depends(_upload_service),
    current_user: User = Depends(get_current_user),
) -> RecipeRead:
    return await service.attach_recipe_photo(recipe_id, data, current_user.id)


@router.post("/{upload_id}/confirm", response_model=UploadStatusRead)
async def confirm_upload(
    upload_id: uuid.UUID,
    service: UploadService = Depends(_upload_service),
    current_user: User = Depends(get_current_user),
) -> UploadStatusRead:
    return await service.confirm_upload(upload_id, current_user.id)


@router.get("/status/{upload_id}", response_model=UploadStatusRead)
async def get_upload_status(
    upload_id: uuid.UUID,
    service: UploadService = Depends(_upload_service),
    current_user: User = Depends(get_current_user),
) -> UploadStatusRead:
    return await service.get_upload_status(upload_id, current_user.id)


@router.delete("/recipes/{recipe_id}/photo", status_code=204)
async def delete_recipe_photo(
    recipe_id: uuid.UUID,
    service: UploadService = Depends(_upload_service),
    current_user: User = Depends(get_current_user),
) -> None:
    await service.delete_recipe_photo(recipe_id, current_user.id)


@router.post("/avatar", response_model=UserRead)
async def set_avatar(
    data: AttachPhotoRequest,
    service: UploadService = Depends(_upload_service),
    current_user: User = Depends(get_current_user),
) -> UserRead:
    return await service.set_avatar(data, current_user.id)


@router.get("/view")
async def view_photo(key: str) -> RedirectResponse:
    bucket = settings.s3_bucket_photos
    url = presign_get(bucket, key)
    return RedirectResponse(url=url, status_code=302)
