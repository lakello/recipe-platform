import uuid
from datetime import UTC, datetime, timedelta
from typing import Literal, cast

from botocore.exceptions import ClientError
from fastapi import HTTPException

from app.core.config import settings
from app.core.storage import (
    ALLOWED_CONTENT_TYPES,
    CONTENT_TYPE_EXTENSIONS,
    delete_object,
    head_object,
    presign_post,
    public_url,
)
from app.models.photo import UploadIntent
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
from app.tasks.thumbnails import validate_upload


class UploadService:
    def __init__(
        self,
        photo_repo: PhotoRepository,
        recipe_repo: RecipeRepository,
        user_repo: UserRepository,
    ) -> None:
        self.photo_repo = photo_repo
        self.recipe_repo = recipe_repo
        self.user_repo = user_repo

    async def presign_upload(
        self, request: PresignRequest, current_user_id: uuid.UUID
    ) -> PresignResponse:
        if request.content_type not in ALLOWED_CONTENT_TYPES:
            raise HTTPException(status_code=422, detail="Unsupported file type")

        ext = CONTENT_TYPE_EXTENSIONS[request.content_type]

        if request.upload_type == "recipe_photo":
            if not request.recipe_id:
                raise HTTPException(status_code=422, detail="recipe_id required")
            recipe = await self.recipe_repo.get_by_id(request.recipe_id)
            if not recipe or recipe.author_id != current_user_id:
                raise HTTPException(status_code=403, detail="Access denied")
            key = f"recipe-photos/{request.recipe_id}/{uuid.uuid4()}.{ext}"
            bucket = settings.s3_bucket_photos
        else:
            key = f"avatars/{current_user_id}/{uuid.uuid4()}.{ext}"
            bucket = settings.s3_bucket_avatars

        intent = await self.photo_repo.create_intent(
            UploadIntent(
                user_id=current_user_id,
                recipe_id=request.recipe_id,
                upload_type=request.upload_type,
                bucket=bucket,
                object_key=key,
                expected_content_type=request.content_type,
                expires_at=datetime.now(UTC)
                + timedelta(minutes=settings.upload_intent_ttl_minutes),
            )
        )
        post = presign_post(
            bucket,
            key,
            request.content_type,
            settings.upload_max_bytes,
        )
        return PresignResponse(
            upload_id=intent.id,
            upload_url=str(post["url"]),
            fields=dict(post["fields"]),
            key=key,
        )

    async def confirm_upload(
        self, upload_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> UploadStatusRead:
        intent = await self._owned_intent(upload_id, current_user_id)
        if intent.status != "pending" or intent.expires_at < datetime.now(UTC):
            raise HTTPException(status_code=409, detail="Upload is not pending")
        self._validate_prefix(intent)

        try:
            metadata = head_object(intent.bucket, intent.object_key)
        except ClientError as exc:
            raise HTTPException(
                status_code=404, detail="Uploaded object not found"
            ) from exc

        if (
            int(metadata.get("ContentLength", 0)) > settings.upload_max_bytes
            or metadata.get("ContentType") != intent.expected_content_type
        ):
            delete_object(intent.bucket, intent.object_key)
            await self.photo_repo.set_intent_status(intent, "failed")
            raise HTTPException(status_code=422, detail="Uploaded object is invalid")

        await self.photo_repo.set_intent_status(intent, "validating")
        validate_upload.delay(str(intent.id))
        return UploadStatusRead(upload_id=intent.id, status="validating")

    async def get_upload_status(
        self, upload_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> UploadStatusRead:
        intent = await self._owned_intent(upload_id, current_user_id)
        status = cast(
            Literal["pending", "validating", "validated", "failed", "attached"],
            intent.status,
        )
        return UploadStatusRead(upload_id=intent.id, status=status)

    async def attach_recipe_photo(
        self,
        recipe_id: uuid.UUID,
        data: AttachPhotoRequest,
        current_user_id: uuid.UUID,
    ) -> RecipeRead:
        recipe = await self.recipe_repo.get_by_id(recipe_id)
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")
        if recipe.author_id != current_user_id:
            raise HTTPException(status_code=403, detail="Access denied")

        intent = await self._owned_intent(data.upload_id, current_user_id)
        if (
            intent.status != "validated"
            or intent.upload_type != "recipe_photo"
            or intent.recipe_id != recipe_id
        ):
            raise HTTPException(status_code=409, detail="Upload is not validated")
        self._validate_prefix(intent)
        await self.photo_repo.upsert(
            recipe_id, intent.object_key, intent.expected_content_type
        )
        await self.photo_repo.set_intent_status(intent, "attached")

        await self.recipe_repo.session.refresh(recipe)
        return RecipeRead.model_validate(recipe)

    async def delete_recipe_photo(
        self, recipe_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> None:
        recipe = await self.recipe_repo.get_by_id(recipe_id)
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")
        if recipe.author_id != current_user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        photo = await self.photo_repo.get_by_recipe(recipe_id)
        if photo:
            await self.photo_repo.delete(photo)

    async def set_avatar(
        self, data: AttachPhotoRequest, current_user_id: uuid.UUID
    ) -> UserRead:
        user = await self.user_repo.get_by_id(current_user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        intent = await self._owned_intent(data.upload_id, current_user_id)
        if intent.status != "validated" or intent.upload_type != "avatar":
            raise HTTPException(status_code=409, detail="Upload is not validated")
        self._validate_prefix(intent)
        avatar = public_url(settings.s3_bucket_avatars, intent.object_key)
        user.avatar_url = avatar
        await self.user_repo.session.commit()
        await self.user_repo.session.refresh(user)
        await self.photo_repo.set_intent_status(intent, "attached")
        return UserRead.model_validate(user)

    async def _owned_intent(
        self, upload_id: uuid.UUID, current_user_id: uuid.UUID
    ) -> UploadIntent:
        intent = await self.photo_repo.get_intent(upload_id)
        if not intent:
            raise HTTPException(status_code=404, detail="Upload not found")
        if intent.user_id != current_user_id:
            raise HTTPException(status_code=403, detail="Access denied")
        return intent

    def _validate_prefix(self, intent: UploadIntent) -> None:
        owner = (
            intent.recipe_id
            if intent.upload_type == "recipe_photo"
            else intent.user_id
        )
        prefix = (
            f"recipe-photos/{owner}/"
            if intent.upload_type == "recipe_photo"
            else f"avatars/{owner}/"
        )
        expected_bucket = (
            settings.s3_bucket_photos
            if intent.upload_type == "recipe_photo"
            else settings.s3_bucket_avatars
        )
        if intent.bucket != expected_bucket or not intent.object_key.startswith(prefix):
            raise HTTPException(status_code=403, detail="Invalid upload target")
