import uuid
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
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


def _oauth_service(session: AsyncSession = Depends(get_db)) -> OAuthService:
    return OAuthService(
        user_repo=UserRepository(session),
        token_repo=RefreshTokenRepository(session),
        oauth_repo=OAuthAccountRepository(session),
    )


def _error_redirect(message: str) -> RedirectResponse:
    params = urlencode({"error": "oauth_error", "message": message})
    response = RedirectResponse(url=f"{settings.frontend_url}/login?{params}")
    response.delete_cookie(_COOKIE_NAME)
    return response


def _success_redirect(tokens: TokenResponse) -> RedirectResponse:
    response = RedirectResponse(url=settings.frontend_url)
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
    response.delete_cookie(_COOKIE_NAME)
    return response


# --- Google ---


@router.get("/google/login")
async def google_login() -> RedirectResponse:
    state = str(uuid.uuid4())
    response = RedirectResponse(url=_build_google_url(state))
    response.set_cookie(
        key=_COOKIE_NAME,
        value=state,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=_COOKIE_MAX_AGE,
    )
    return response


@router.get("/google/callback")
async def google_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    service: OAuthService = Depends(_oauth_service),
) -> RedirectResponse:
    if error or not code or not state:
        return _error_redirect(error or "Authorization denied")
    stored_state = request.cookies.get(_COOKIE_NAME)
    try:
        tokens = await service.handle_google_callback(code, state, stored_state)
    except Exception as exc:
        return _error_redirect(str(exc))
    return _success_redirect(tokens)


# --- Yandex ---


@router.get("/yandex/login")
async def yandex_login() -> RedirectResponse:
    state = str(uuid.uuid4())
    response = RedirectResponse(url=_build_yandex_url(state))
    response.set_cookie(
        key=_COOKIE_NAME,
        value=state,
        httponly=True,
        secure=settings.cookie_secure,
        samesite="lax",
        max_age=_COOKIE_MAX_AGE,
    )
    return response


@router.get("/yandex/callback")
async def yandex_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    service: OAuthService = Depends(_oauth_service),
) -> RedirectResponse:
    if error or not code or not state:
        return _error_redirect(error or "Authorization denied")
    stored_state = request.cookies.get(_COOKIE_NAME)
    try:
        tokens = await service.handle_yandex_callback(code, state, stored_state)
    except Exception as exc:
        return _error_redirect(str(exc))
    return _success_redirect(tokens)
