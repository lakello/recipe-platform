import uuid
from datetime import UTC, datetime

from sqlalchemy import select, update
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

    async def get_by_token(self, token: str) -> RefreshToken | None:
        result = await self.session.execute(
            select(RefreshToken).where(RefreshToken.token == token)
        )
        return result.scalar_one_or_none()
    
    async def revoke(self, token: str) -> None:
        await self.session.execute(
            update(RefreshToken)
            .where(RefreshToken.token == token)
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

    async def is_valid(self, token: str) -> bool:
        record = await self.get_by_token(token)
        if not record:
            return False
        if record.is_revoked:
            return False
        if record.expires_at.replace(tzinfo=UTC) < datetime.now(UTC):
            return False
        return True
