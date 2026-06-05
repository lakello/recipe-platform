import uuid

from fastapi import HTTPException

from app.core.config import settings
from app.core.storage import (
    ALLOWED_CONTENT_TYPES,
    CONTENT_TYPE_EXTENSIONS,
    presign_put,
    public_url,
)
from app.repositories.photo import PhotoRepository
from app.repositories.recipe import RecipeRepository
from app.repositories.user import UserRepository
from app.schemas.recipe import RecipeRead
from app.schemas.upload import AttachPhotoRequest, PresignRequest, PresignResponse
from app.schemas.user import UserRead
from app.tasks.thumbnails import generate_thumbnail


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

        upload_url = presign_put(bucket, key, request.content_type)
        return PresignResponse(upload_url=upload_url, key=key)

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

        content_type = self._guess_content_type(data.key)
        photo = await self.photo_repo.upsert(recipe_id, data.key, content_type)

        generate_thumbnail.delay(str(photo.id), data.key)

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

    async def set_avatar(self, key: str, current_user_id: uuid.UUID) -> UserRead:
        user = await self.user_repo.get_by_id(current_user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        avatar = public_url(settings.s3_bucket_avatars, key)
        user.avatar_url = avatar
        await self.user_repo.session.commit()
        await self.user_repo.session.refresh(user)
        return UserRead.model_validate(user)

    def _guess_content_type(self, key: str) -> str:
        ext_map = {
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "png": "image/png",
            "webp": "image/webp",
        }
        ext = key.rsplit(".", 1)[-1].lower()
        return ext_map.get(ext, "image/jpeg")
