import asyncio

from app.celery_app import celery_app


@celery_app.task(name="tasks.cleanup_refresh_tokens")  # type: ignore[misc]
def cleanup_refresh_tokens() -> None:
    from app.db.session import async_session_factory
    from app.repositories.refresh_token import RefreshTokenRepository

    async def _run() -> None:
        async with async_session_factory() as session:
            await RefreshTokenRepository(session).delete_expired_or_revoked()

    asyncio.run(_run())
