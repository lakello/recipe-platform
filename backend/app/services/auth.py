import uuid
from datetime import UTC, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_refresh_token,
)
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
        expires_at = datetime.now(UTC) + timedelta(
            days=settings.jwt_refresh_token_expire_days
        )
        await self.token_repo.create(
            RefreshToken(
                user_id=user_id,
                token_hash=hash_refresh_token(refresh_token),
                family_id=uuid.uuid4(),
                expires_at=expires_at,
            )
        )
        return TokenResponse(access_token=access_token, refresh_token=refresh_token)

    async def register(self, data: RegisterRequest) -> TokenResponse:
        if await self.user_repo.get_by_email(data.email):
            raise HTTPException(status_code=409, detail="Email already registered")
        if await self.user_repo.get_by_username(data.username):
            raise HTTPException(status_code=409, detail="Username already taken")
        try:
            user = await self.user_repo.create(
                User(
                    email=data.email,
                    username=data.username,
                    password_hash=_hash_password(data.password),
                )
            )
            tokens = await self._issue_tokens(user.id)
            await self.user_repo.session.commit()
            return tokens
        except IntegrityError as exc:
            await self.user_repo.session.rollback()
            raise HTTPException(
                status_code=409, detail="Email or username already registered"
            ) from exc

    async def login(self, data: LoginRequest) -> TokenResponse:
        user = await self.user_repo.get_by_email(data.email)
        if not user or not verify_password(data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        if not user.is_active:
            raise HTTPException(status_code=403, detail="Account is disabled")
        tokens = await self._issue_tokens(user.id)
        await self.user_repo.session.commit()
        return tokens

    async def refresh(self, refresh_token: str) -> TokenResponse:
        replacement_token = create_refresh_token()
        rotated = await self.token_repo.rotate(
            hash_refresh_token(refresh_token),
            hash_refresh_token(replacement_token),
            datetime.now(UTC) + timedelta(days=settings.jwt_refresh_token_expire_days),
        )
        if not rotated:
            raise HTTPException(
                status_code=401, detail="Invalid or expired refresh token"
            )
        return TokenResponse(
            access_token=create_access_token(rotated.user_id),
            refresh_token=replacement_token,
        )

    async def logout(self, refresh_token: str) -> None:
        await self.token_repo.revoke(hash_refresh_token(refresh_token))
        await self.token_repo.session.commit()
