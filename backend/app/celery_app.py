from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "recipe_platform",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend_url,
    include=["app.tasks.thumbnails", "app.tasks.shopping_list", "app.tasks.email"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    result_expires=3600,
    timezone="UTC",
    enable_utc=True,
    beat_schedule={},
)
