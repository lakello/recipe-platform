import logging

from app.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="tasks.generate_thumbnail")
def generate_thumbnail(photo_id: str, source_key: str) -> None:
    """Generate thumbnail for a recipe photo stored in object storage."""
    logger.info("Generating thumbnail for photo %s (key: %s)", photo_id, source_key)
    # Будет реализовано в задаче "Фото рецептов и аватары"
