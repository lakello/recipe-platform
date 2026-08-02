from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth_cookies import clear_auth_cookies, set_auth_cookies
from app.core.rate_limit import client_ip, enforce, opaque
from app.db.session import get_db
from app.repositories.refresh_token import RefreshTokenRepository
from app.repositories.user import UserRepository
from app.schemas.auth import (
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    WebAuthResponse,
)
from app.services.auth import AuthService

router = APIRouter(prefix="/api/auth", tags=["auth"])


def _auth_service(session: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(
        user_repo=UserRepository(session),
        token_repo=RefreshTokenRepository(session),
    )


async def _limit_register(request: Request) -> None:
    await enforce(request, "register", client_ip(request), 5)


async def _limit_login(request: Request, data: LoginRequest) -> None:
    await enforce(request, "login-ip", client_ip(request), 10)
    await enforce(request, "login-account", opaque(data.email), 5)


async def _limit_refresh(request: Request) -> None:
    await enforce(request, "refresh", client_ip(request), 30)


@router.post("/register", response_model=WebAuthResponse, status_code=201)
async def register(
    data: RegisterRequest,
    response: Response,
    _: None = Depends(_limit_register),
    service: AuthService = Depends(_auth_service),
) -> WebAuthResponse:
    tokens = await service.register(data)
    return WebAuthResponse(csrf_token=set_auth_cookies(response, tokens))


@router.post("/login", response_model=WebAuthResponse)
async def login(
    data: LoginRequest,
    response: Response,
    _: None = Depends(_limit_login),
    service: AuthService = Depends(_auth_service),
) -> WebAuthResponse:
    tokens = await service.login(data)
    return WebAuthResponse(csrf_token=set_auth_cookies(response, tokens))


@router.post("/refresh", response_model=WebAuthResponse)
async def refresh(
    request: Request,
    response: Response,
    _: None = Depends(_limit_refresh),
    service: AuthService = Depends(_auth_service),
) -> WebAuthResponse:
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(status_code=401, detail="Refresh token not found")
    tokens = await service.refresh(token)
    return WebAuthResponse(csrf_token=set_auth_cookies(response, tokens))


@router.post("/logout", status_code=204)
async def logout(
    request: Request,
    response: Response,
    service: AuthService = Depends(_auth_service),
) -> None:
    token = request.cookies.get("refresh_token")
    if token:
        await service.logout(token)
    clear_auth_cookies(response)


@router.post("/token/register", response_model=TokenResponse, status_code=201)
async def token_register(
    data: RegisterRequest,
    request: Request,
    _: None = Depends(_limit_register),
    service: AuthService = Depends(_auth_service),
) -> TokenResponse:
    return await service.register(data)


@router.post("/token/login", response_model=TokenResponse)
async def token_login(
    data: LoginRequest,
    request: Request,
    _: None = Depends(_limit_login),
    service: AuthService = Depends(_auth_service),
) -> TokenResponse:
    return await service.login(data)


@router.post("/token/refresh", response_model=TokenResponse)
async def token_refresh(
    data: RefreshRequest,
    request: Request,
    _: None = Depends(_limit_refresh),
    service: AuthService = Depends(_auth_service),
) -> TokenResponse:
    return await service.refresh(data.refresh_token)


@router.post("/token/logout", status_code=204)
async def token_logout(
    data: RefreshRequest,
    service: AuthService = Depends(_auth_service),
) -> None:
    await service.logout(data.refresh_token)
