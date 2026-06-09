import asyncio
import uuid
from datetime import date
from typing import Literal, cast

from app.celery_app import celery_app


@celery_app.task(name="tasks.generate_shopping_list")  # type: ignore[misc]
def generate_shopping_list_task(
    user_id: str, mode: str, dates: list[str] | None = None
) -> None:
    import app.models  # noqa: F401
    from app.db.session import async_session_factory
    from app.repositories.shopping_list import ShoppingListRepository
    from app.schemas.shopping_list import GenerateRequest
    from app.services.shopping_list import ShoppingListService

    parsed_dates = [date.fromisoformat(d) for d in dates] if dates else None
    typed_mode = cast(Literal["today", "week", "custom"], mode)

    async def _run() -> None:
        async with async_session_factory() as session:
            service = ShoppingListService(ShoppingListRepository(session))
            await service.generate(
                uuid.UUID(user_id),
                GenerateRequest(mode=typed_mode, dates=parsed_dates),
            )

    asyncio.run(_run())
