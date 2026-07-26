import uuid
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken
from app.repositories.refresh_token import RefreshTokenRepository


def make_record(*, revoked: bool = False, expired: bool = False) -> RefreshToken:
    record = MagicMock(spec=RefreshToken)
    record.user_id = uuid.uuid4()
    record.family_id = uuid.uuid4()
    record.is_revoked = revoked
    delta = timedelta(days=-1 if expired else 1)
    record.expires_at = datetime.now(UTC) + delta
    return record


def make_session(record: RefreshToken | None) -> AsyncMock:
    session = AsyncMock(spec=AsyncSession)
    result = MagicMock()
    result.scalar_one_or_none.return_value = record
    session.execute.return_value = result
    return session


async def test_rotate_revokes_and_replaces_in_one_transaction() -> None:
    record = make_record()
    session = make_session(record)
    repository = RefreshTokenRepository(session)

    replacement = await repository.rotate(
        "old-hash", "new-hash", datetime.now(UTC) + timedelta(days=30)
    )

    assert record.is_revoked is True
    assert replacement is not None
    assert replacement.user_id == record.user_id
    assert replacement.family_id == record.family_id
    assert replacement.token_hash == "new-hash"
    session.begin.assert_called_once()
    statement = session.execute.call_args.args[0]
    assert statement._for_update_arg is not None


async def test_reuse_revokes_token_family() -> None:
    session = make_session(make_record(revoked=True))
    repository = RefreshTokenRepository(session)

    replacement = await repository.rotate(
        "reused-hash", "new-hash", datetime.now(UTC) + timedelta(days=30)
    )

    assert replacement is None
    assert session.execute.await_count == 2


async def test_expired_token_is_revoked() -> None:
    record = make_record(expired=True)
    repository = RefreshTokenRepository(make_session(record))

    replacement = await repository.rotate(
        "expired-hash", "new-hash", datetime.now(UTC) + timedelta(days=30)
    )

    assert replacement is None
    assert record.is_revoked is True


async def test_cleanup_deletes_records_after_their_ttl() -> None:
    session = make_session(None)
    session.execute.return_value.rowcount = 2
    repository = RefreshTokenRepository(session)

    assert await repository.delete_expired_or_revoked() == 2
    session.flush.assert_awaited_once()
