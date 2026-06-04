import uuid
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException

from app.core.security import create_access_token, create_refresh_token
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.repositories.refresh_token import RefreshTokenRepository
from app.repositories.user import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.services.user import _hash_password, verify_password


class AuthService:
    def __init__(
        self,
        user_repo: UserRepository,
        token_repo: RefreshTokenRepository,
    ) -> None:
        self.user_repo = user_repo
        self.token_repo = token_repo

    async def _issue_tokens(self, user_id: uuid.UUID) -> TokenResponse:
        access_token = create_access_token(user_id)
        refresh_token = create_refresh_token()
        expires_at = datetime.now(UTC) + timedelta(days=30)
        await self.token_repo.create(
            RefreshToken(
                user_id=user_id,
                token=refresh_token,
                expires_at=expires_at,
            )
        )
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    async def register(self, data: RegisterRequest) -> TokenResponse:
        if await self.user_repo.get_by_email(data.email):
            raise HTTPException(status_code=409, detail="Email already registered")
        if await self.user_repo.get_by_username(data.username):
            raise HTTPException(status_code=409, detail="Username already taken")
        user = await self.user_repo.create(
            User(
                email=data.email,
                username=data.username,
                password_hash=_hash_password(data.password),
            )
        )
        return await self._issue_tokens(user.id)

    async def login(self, data: LoginRequest) -> TokenResponse:
        user = await self.user_repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        if not user.is_active:
            raise HTTPException(status_code=403, detail="Account is disabled")
        return await self._issue_tokens(user.id)

    async def refresh(self, refresh_token: str) -> TokenResponse:
        if not await self.token_repo.is_valid(refresh_token):
            raise HTTPException(
                status_code=401, detail="Invalid or expired refresh token"
            )
        record = await self.token_repo.get_by_token(refresh_token)
        await self.token_repo.revoke(refresh_token)
        return await self._issue_tokens(record.user_id)  # type: ignore[union-attr]

    async def logout(self, refresh_token: str) -> None:
        await self.token_repo.revoke(refresh_token)
