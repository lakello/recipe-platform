from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.oauth_account import UserOAuthAccount


class OAuthAccountRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_provider(
        self, provider: str, provider_user_id: str
    ) -> UserOAuthAccount | None:
        result = await self.session.execute(
            select(UserOAuthAccount).where(
                UserOAuthAccount.provider == provider,
                UserOAuthAccount.provider_user_id == provider_user_id,
            )
        )
        return result.scalar_one_or_none()

    async def create(self, account: UserOAuthAccount) -> UserOAuthAccount:
        self.session.add(account)
        await self.session.commit()
        await self.session.refresh(account)
        return account
