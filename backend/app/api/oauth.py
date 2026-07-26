import secrets
import uuid
from urllib.parse import urlencode

import aiohttp
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth_cookies import set_auth_cookies
from app.core.config import settings
from app.core.rate_limit import client_ip, enforce
from app.db.session import get_db
from app.repositories.oauth_account import OAuthAccountRepository
from app.repositories.refresh_token import RefreshTokenRepository
from app.repositories.user import UserRepository
from app.schemas.auth import TokenResponse
from app.services.oauth import OAuthService


def _build_google_url(state: str) -> str:
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "online",
    }
    return "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)


def _build_yandex_url(state: str) -> str:
    params = {
        "client_id": settings.yandex_client_id,
        "redirect_uri": settings.yandex_redirect_uri,
        "response_type": "code",
        "state": state,
    }
    return "https://oauth.yandex.ru/authorize?" + urlencode(params)


router = APIRouter(prefix="/api/auth", tags=["auth"])

_COOKIE_NAME = "oauth_state"
_COOKIE_MAX_AGE = 300  # 5 minutes


def _oauth_service(
    request: Request, session: AsyncSession = Depends(get_db)
) -> OAuthService:
    return OAuthService(
        user_repo=UserRepository(session),
        token_repo=RefreshTokenRepository(session),
        oauth_repo=OAuthAccountRepository(session),
        http_session=request.app.state.oauth_session,
    )


def _delete_state_cookie(response: RedirectResponse) -> None:
    response.delete_cookie(
        _COOKIE_NAME, path="/api/auth", domain=settings.cookie_domain
    )


def _error_redirect() -> RedirectResponse:
    params = urlencode({"error": "oauth_error"})
    response = RedirectResponse(url=f"{settings.frontend_url}/login?{params}")
    _delete_state_cookie(response)
    return response


def _success_redirect(tokens: TokenResponse) -> RedirectResponse:
    response = RedirectResponse(url=settings.frontend_url)
    set_auth_cookies(response, tokens)
    _delete_state_cookie(response)
    return response


async def _limit_oauth(request: Request) -> None:
    await enforce(request, "oauth", client_ip(request), 20)


async def _save_state(request: Request, state: str) -> None:
    await request.app.state.redis.set(
        f"oauth-state:{state}", "1", ex=_COOKIE_MAX_AGE, nx=True
    )


async def _consume_state(request: Request, state: str | None) -> bool:
    stored_state = request.cookies.get(_COOKIE_NAME)
    if not state or not stored_state or not secrets.compare_digest(state, stored_state):
        return False
    return bool(await request.app.state.redis.getdel(f"oauth-state:{state}"))


@router.get("/google/login", dependencies=[Depends(_limit_oauth)])
async def google_login(request: Request) -> RedirectResponse:
    state = str(uuid.uuid4())
    await _save_state(request, state)
    response = RedirectResponse(url=_build_google_url(state))
    response.set_cookie(
        key=_COOKIE_NAME,
        value=state,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=_COOKIE_MAX_AGE,
        path="/api/auth",
        domain=settings.cookie_domain,
    )
    return response


@router.get("/google/callback")
async def google_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    service: OAuthService = Depends(_oauth_service),
    _: None = Depends(_limit_oauth),
) -> RedirectResponse:
    valid_state = await _consume_state(request, state)
    if error or not code or not valid_state:
        return _error_redirect()
    try:
        tokens = await service.handle_google_callback(code)
    except (aiohttp.ClientError, HTTPException, TimeoutError, KeyError, ValueError):
        return _error_redirect()
    return _success_redirect(tokens)


@router.get("/yandex/login", dependencies=[Depends(_limit_oauth)])
async def yandex_login(request: Request) -> RedirectResponse:
    state = str(uuid.uuid4())
    await _save_state(request, state)
    response = RedirectResponse(url=_build_yandex_url(state))
    response.set_cookie(
        key=_COOKIE_NAME,
        value=state,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=_COOKIE_MAX_AGE,
        path="/api/auth",
        domain=settings.cookie_domain,
    )
    return response


@router.get("/yandex/callback")
async def yandex_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    service: OAuthService = Depends(_oauth_service),
    _: None = Depends(_limit_oauth),
) -> RedirectResponse:
    valid_state = await _consume_state(request, state)
    if error or not code or not valid_state:
        return _error_redirect()
    try:
        tokens = await service.handle_yandex_callback(code)
    except (aiohttp.ClientError, HTTPException, TimeoutError, KeyError, ValueError):
        return _error_redirect()
    return _success_redirect(tokens)
