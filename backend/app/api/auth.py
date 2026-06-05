from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.repositories.refresh_token import RefreshTokenRepository
from app.repositories.user import UserRepository
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from app.services.auth import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _auth_service(session: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(
        user_repo=UserRepository(session),
        token_repo=RefreshTokenRepository(session),
    )


def _set_auth_cookies(response: Response, tokens: TokenResponse) -> None:
    response.set_cookie(
        key="access_token",
        value=tokens.access_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=settings.jwt_access_token_expire_minutes * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=tokens.refresh_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=settings.jwt_refresh_token_expire_days * 24 * 60 * 60,
    )


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(
    data: RegisterRequest,
    response: Response,
    service: AuthService = Depends(_auth_service),
) -> TokenResponse:
    tokens = await service.register(data)
    _set_auth_cookies(response, tokens)
    return tokens


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest,
    response: Response,
    service: AuthService = Depends(_auth_service),
) -> TokenResponse:
    tokens = await service.login(data)
    _set_auth_cookies(response, tokens)
    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    request: Request,
    response: Response,
    data: RefreshRequest | None = None,
    service: AuthService = Depends(_auth_service),
) -> TokenResponse:
    token = data.refresh_token if data else request.cookies.get("refresh_token")
    if not token:
        from fastapi import HTTPException

        raise HTTPException(status_code=401, detail="Refresh token not found")
    tokens = await service.refresh(token)
    _set_auth_cookies(response, tokens)
    return tokens


@router.post("/logout", status_code=204)
async def logout(
    request: Request,
    response: Response,
    data: RefreshRequest | None = None,
    service: AuthService = Depends(_auth_service),
) -> None:
    token = data.refresh_token if data else request.cookies.get("refresh_token")
    if token:
        await service.logout(token)
    _clear_auth_cookies(response)
