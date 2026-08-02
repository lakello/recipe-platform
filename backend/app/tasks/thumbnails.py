import asyncio
import io
import logging
import uuid
import warnings
from datetime import UTC, datetime

from PIL import Image

from app.celery_app import celery_app
from app.core.config import settings
from app.core.storage import delete_object, get_object_bytes, put_object

logger = logging.getLogger(__name__)

_FORMAT_CONTENT_TYPES = {
    "JPEG": "image/jpeg",
    "PNG": "image/png",
    "WEBP": "image/webp",
}


def sanitize_image(data: bytes, expected_content_type: str) -> bytes:
    Image.MAX_IMAGE_PIXELS = settings.upload_max_pixels
    with warnings.catch_warnings():
        warnings.simplefilter("error", Image.DecompressionBombWarning)
        with Image.open(io.BytesIO(data)) as image:
            image.verify()
        with Image.open(io.BytesIO(data)) as image:
            image.load()
            if image.width * image.height > settings.upload_max_pixels:
                raise ValueError("Image pixel limit exceeded")
            image_format = image.format
            if not image_format:
                raise ValueError("Unknown image format")
            if _FORMAT_CONTENT_TYPES.get(image_format) != expected_content_type:
                raise ValueError("Image content does not match declared type")
            clean = image.convert("RGB") if image_format == "JPEG" else image.copy()

    output = io.BytesIO()
    clean.save(output, format=image_format)
    return output.getvalue()


@celery_app.task(name="tasks.validate_upload")  # type: ignore[misc]
def validate_upload(upload_id: str) -> None:
    from app.db.session import async_session_factory
    from app.repositories.photo import PhotoRepository

    async def _run() -> None:
        async with async_session_factory() as session:
            repository = PhotoRepository(session)
            intent = await repository.get_intent_for_update(uuid.UUID(upload_id))
            if not intent or intent.status != "validating":
                return
            try:
                sanitized = sanitize_image(
                    get_object_bytes(intent.bucket, intent.object_key),
                    intent.expected_content_type,
                )
                put_object(
                    intent.bucket,
                    intent.object_key,
                    sanitized,
                    intent.expected_content_type,
                )
                await repository.set_intent_status(intent, "validated")
                await session.commit()
            except Exception:
                logger.exception("Upload validation failed for %s", upload_id)
                delete_object(intent.bucket, intent.object_key)
                await repository.set_intent_status(intent, "failed")
                await session.commit()

    asyncio.run(_run())


@celery_app.task(name="tasks.cleanup_uploads")  # type: ignore[misc]
def cleanup_uploads() -> None:
    from app.db.session import async_session_factory
    from app.repositories.photo import PhotoRepository

    async def _run() -> None:
        async with async_session_factory() as session:
            intents = await PhotoRepository(session).delete_stale_intents(
                datetime.now(UTC)
            )
            await session.commit()
            for intent in intents:
                delete_object(intent.bucket, intent.object_key)

    asyncio.run(_run())
