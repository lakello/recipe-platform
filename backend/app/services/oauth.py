import re
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import aiohttp
from fastapi import HTTPException

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token
from app.models.oauth_account import UserOAuthAccount
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.repositories.oauth_account import OAuthAccountRepository
from app.repositories.refresh_token import RefreshTokenRepository
from app.repositories.user import UserRepository
from app.schemas.auth import TokenResponse


@dataclass
class OAuthUserInfo:
    provider_user_id: str
    email: str
    name: str


class OAuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        token_repo: RefreshTokenRepository,
        oauth_repo: OAuthAccountRepository,
    ) -> None:
        self.user_repo = user_repo
        self.token_repo = token_repo
        self.oauth_repo = oauth_repo

    # --- Google ---

    async def _exchange_google_code(self, code: str) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "redirect_uri": settings.google_redirect_uri,
                    "grant_type": "authorization_code",
                },
            ) as resp:
                if resp.status != 200:
                    raise HTTPException(
                        status_code=502, detail="Google token exchange failed"
                    )
                data = await resp.json()
                return str(data["access_token"])

    async def _get_google_user_info(self, access_token: str) -> OAuthUserInfo:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"},
            ) as resp:
                if resp.status != 200:
                    raise HTTPException(
                        status_code=502, detail="Google userinfo request failed"
                    )
                data = await resp.json()
                email = data.get("email")
                if not email:
                    raise HTTPException(
                        status_code=400, detail="Google account has no email"
                    )
                return OAuthUserInfo(
                    provider_user_id=data["id"],
                    email=email,
                    name=data.get("name", ""),
                )

    async def handle_google_callback(
        self, code: str, state: str, stored_state: str | None
    ) -> TokenResponse:
        if not stored_state or state != stored_state:
            raise HTTPException(status_code=400, detail="Invalid OAuth state")
        access_token = await self._exchange_google_code(code)
        user_info = await self._get_google_user_info(access_token)
        return await self._get_or_create_user(user_info, provider="google")

    # --- Yandex ---

    async def _exchange_yandex_code(self, code: str) -> str:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://oauth.yandex.ru/token",
                data={
                    "code": code,
                    "client_id": settings.yandex_client_id,
                    "client_secret": settings.yandex_client_secret,
                    "redirect_uri": settings.yandex_redirect_uri,
                    "grant_type": "authorization_code",
                },
            ) as resp:
                if resp.status != 200:
                    raise HTTPException(
                        status_code=502, detail="Yandex token exchange failed"
                    )
                data = await resp.json()
                return str(data["access_token"])

    async def _get_yandex_user_info(self, access_token: str) -> OAuthUserInfo:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://login.yandex.ru/info?format=json",
                headers={"Authorization": f"OAuth {access_token}"},
            ) as resp:
                if resp.status != 200:
                    raise HTTPException(
                        status_code=502, detail="Yandex userinfo request failed"
                    )
                data = await resp.json()
                email = data.get("default_email") or (data.get("emails") or [None])[0]
                if not email:
                    raise HTTPException(
                        status_code=400, detail="Yandex account has no email"
                    )
                name = data.get("real_name") or data.get("display_name") or ""
                return OAuthUserInfo(
                    provider_user_id=str(data["id"]),
                    email=email,
                    name=name,
                )

    async def handle_yandex_callback(
        self, code: str, state: str, stored_state: str | None
    ) -> TokenResponse:
        if not stored_state or state != stored_state:
            raise HTTPException(status_code=400, detail="Invalid OAuth state")
        access_token = await self._exchange_yandex_code(code)
        user_info = await self._get_yandex_user_info(access_token)
        return await self._get_or_create_user(user_info, provider="yandex")

    # --- Shared logic ---

    async def _get_or_create_user(
        self, user_info: OAuthUserInfo, provider: str
    ) -> TokenResponse:
        oauth_account = await self.oauth_repo.get_by_provider(
            provider, user_info.provider_user_id
        )
        if oauth_account:
            user = await self.user_repo.get_by_id(oauth_account.user_id)
            if not user or not user.is_active:
                raise HTTPException(status_code=403, detail="Account is disabled")
            return await self._issue_tokens(user.id)

        # Link to existing account by email, or create new user
        user = await self.user_repo.get_by_email(user_info.email)
        if not user:
            username = await self._generate_unique_username(
                user_info.name, user_info.email
            )
            user = await self.user_repo.create(
                User(
                    email=user_info.email,
                    username=username,
                    password_hash=None,
                    is_email_verified=True,
                )
            )

        await self.oauth_repo.create(
            UserOAuthAccount(
                user_id=user.id,
                provider=provider,
                provider_user_id=user_info.provider_user_id,
            )
        )
        return await self._issue_tokens(user.id)

    async def _generate_unique_username(self, name: str, email: str) -> str:
        base = re.sub(r"[^a-z0-9]", "", name.lower()) or email.split("@")[0]
        base = base[:46]
        candidate = base
        if not await self.user_repo.get_by_username(candidate):
            return candidate
        for _ in range(10):
            candidate = f"{base}{uuid.uuid4().hex[:4]}"
            if not await self.user_repo.get_by_username(candidate):
                return candidate
        return f"{base}{uuid.uuid4().hex[:8]}"

    async def _issue_tokens(self, user_id: uuid.UUID) -> TokenResponse:
        access_token = create_access_token(user_id)
        refresh_token = create_refresh_token()
        expires_at = datetime.now(UTC) + timedelta(
            days=settings.jwt_refresh_token_expire_days
        )
        await self.token_repo.create(
            RefreshToken(
                user_id=user_id,
                token=refresh_token,
                expires_at=expires_at,
            )
        )
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)
