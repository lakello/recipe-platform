import io
import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from botocore.exceptions import ClientError
from fastapi import HTTPException
from PIL import Image

from app.core.config import settings
from app.models.photo import UploadIntent
from app.repositories.photo import PhotoRepository
from app.repositories.recipe import RecipeRepository
from app.repositories.user import UserRepository
from app.services.upload import UploadService
from app.tasks.thumbnails import sanitize_image


def make_intent(user_id: uuid.UUID, **kwargs: object) -> UploadIntent:
    intent = MagicMock(spec=UploadIntent)
    defaults = {
        "id": uuid.uuid4(),
        "user_id": user_id,
        "recipe_id": uuid.uuid4(),
        "upload_type": "recipe_photo",
        "bucket": settings.s3_bucket_photos,
        "object_key": "",
        "expected_content_type": "image/jpeg",
        "status": "pending",
        "expires_at": datetime.now(UTC) + timedelta(minutes=10),
    }
    defaults.update(kwargs)
    if not defaults["object_key"]:
        defaults["object_key"] = (
            f"recipe-photos/{defaults['recipe_id']}/{uuid.uuid4()}.jpg"
        )
    for key, value in defaults.items():
        setattr(intent, key, value)
    return intent


@pytest.fixture
def photo_repo() -> AsyncMock:
    return AsyncMock(spec=PhotoRepository)


@pytest.fixture
def service(photo_repo: AsyncMock) -> UploadService:
    return UploadService(
        photo_repo,
        AsyncMock(spec=RecipeRepository),
        AsyncMock(spec=UserRepository),
    )


async def test_rejects_upload_owned_by_another_user(
    service: UploadService, photo_repo: AsyncMock
) -> None:
    photo_repo.get_intent.return_value = make_intent(uuid.uuid4())

    with pytest.raises(HTTPException, match="Access denied") as exc:
        await service.confirm_upload(uuid.uuid4(), uuid.uuid4())

    assert exc.value.status_code == 403


async def test_rejects_invalid_key_prefix(
    service: UploadService, photo_repo: AsyncMock
) -> None:
    user_id = uuid.uuid4()
    photo_repo.get_intent.return_value = make_intent(
        user_id, object_key=f"avatars/{user_id}/foreign.jpg"
    )

    with pytest.raises(HTTPException, match="Invalid upload target") as exc:
        await service.confirm_upload(uuid.uuid4(), user_id)

    assert exc.value.status_code == 403


async def test_rejects_missing_object(
    service: UploadService, photo_repo: AsyncMock
) -> None:
    user_id = uuid.uuid4()
    photo_repo.get_intent.return_value = make_intent(user_id)
    error = ClientError({"Error": {"Code": "404", "Message": "missing"}}, "HeadObject")

    with patch("app.services.upload.head_object", side_effect=error):
        with pytest.raises(HTTPException, match="Uploaded object not found") as exc:
            await service.confirm_upload(uuid.uuid4(), user_id)

    assert exc.value.status_code == 404


async def test_rejects_oversized_object(
    service: UploadService, photo_repo: AsyncMock
) -> None:
    user_id = uuid.uuid4()
    intent = make_intent(user_id)
    photo_repo.get_intent.return_value = intent

    with (
        patch(
            "app.services.upload.head_object",
            return_value={
                "ContentLength": settings.upload_max_bytes + 1,
                "ContentType": "image/jpeg",
            },
        ),
        patch("app.services.upload.delete_object") as delete,
    ):
        with pytest.raises(HTTPException, match="Uploaded object is invalid"):
            await service.confirm_upload(intent.id, user_id)

    delete.assert_called_once_with(intent.bucket, intent.object_key)
    photo_repo.set_intent_status.assert_awaited_once_with(intent, "failed")


def test_rejects_mime_spoofing() -> None:
    data = io.BytesIO()
    Image.new("RGB", (2, 2)).save(data, format="PNG")

    with pytest.raises(ValueError, match="does not match"):
        sanitize_image(data.getvalue(), "image/jpeg")


def test_rejects_excessive_pixel_count(monkeypatch: pytest.MonkeyPatch) -> None:
    data = io.BytesIO()
    Image.new("RGB", (2, 2)).save(data, format="PNG")
    monkeypatch.setattr(settings, "upload_max_pixels", 1)

    with pytest.raises((ValueError, Image.DecompressionBombError)):
        sanitize_image(data.getvalue(), "image/png")


def test_sanitize_image_removes_metadata() -> None:
    data = io.BytesIO()
    exif = Image.Exif()
    exif[0x010E] = "secret"
    Image.new("RGB", (2, 2)).save(
        data,
        format="JPEG",
        exif=exif,
    )

    sanitized = sanitize_image(data.getvalue(), "image/jpeg")

    with Image.open(io.BytesIO(sanitized)) as image:
        assert not image.getexif()
