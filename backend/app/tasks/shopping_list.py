import asyncio
import uuid

from app.celery_app import celery_app


@celery_app.task(name="tasks.generate_shopping_list")
def generate_shopping_list_task(
    user_id: str, mode: str, dates: list[str] | None = None
) -> None:
    import app.models  # noqa: F401 — ensures all SQLAlchemy mappers are resolved
    from app.db.session import async_session_factory
    from app.repositories.shopping_list import ShoppingListRepository
    from app.schemas.shopping_list import GenerateRequest
    from app.services.shopping_list import ShoppingListService

    async def _run() -> None:
        async with async_session_factory() as session:
            service = ShoppingListService(ShoppingListRepository(session))
            await service.generate(
                uuid.UUID(user_id), GenerateRequest(mode=mode, dates=dates)
            )

    asyncio.run(_run())
