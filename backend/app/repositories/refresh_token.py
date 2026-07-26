import uuid
from datetime import UTC, datetime

from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, token: RefreshToken) -> RefreshToken:
        self.session.add(token)
        await self.session.commit()
        await self.session.refresh(token)
        return token

    async def rotate(
        self, token_hash: str, replacement_hash: str, expires_at: datetime
    ) -> RefreshToken | None:
        async with self.session.begin():
            result = await self.session.execute(
                select(RefreshToken)
                .where(RefreshToken.token_hash == token_hash)
                .with_for_update()
            )
            record = result.scalar_one_or_none()
            if not record:
                return None
            if record.is_revoked:
                await self.session.execute(
                    update(RefreshToken)
                    .where(RefreshToken.family_id == record.family_id)
                    .values(is_revoked=True)
                )
                return None
            if record.expires_at < datetime.now(UTC):
                record.is_revoked = True
                return None

            record.is_revoked = True
            replacement = RefreshToken(
                user_id=record.user_id,
                token_hash=replacement_hash,
                family_id=record.family_id,
                expires_at=expires_at,
            )
            self.session.add(replacement)
        return replacement

    async def revoke(self, token_hash: str) -> None:
        await self.session.execute(
            update(RefreshToken)
            .where(RefreshToken.token_hash == token_hash)
            .values(is_revoked=True)
        )
        await self.session.commit()

    async def revoke_all_for_user(self, user_id: uuid.UUID) -> None:
        await self.session.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == user_id, RefreshToken.is_revoked == False)  # noqa: E712
            .values(is_revoked=True)
        )
        await self.session.commit()

    async def delete_expired_or_revoked(self) -> int:
        result = await self.session.execute(
            delete(RefreshToken).where(
                RefreshToken.expires_at < datetime.now(UTC)
            )
        )
        await self.session.commit()
        return int(result.rowcount)  # type: ignore[attr-defined]
