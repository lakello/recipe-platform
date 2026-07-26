import secrets

from fastapi import Response

from app.core.config import settings
from app.schemas.auth import TokenResponse


def set_auth_cookies(response: Response, tokens: TokenResponse) -> str:
    csrf_token = secrets.token_urlsafe(32)
    response.set_cookie(
        "access_token",
        tokens.access_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=settings.jwt_access_token_expire_minutes * 60,
        path="/",
        domain=settings.cookie_domain,
    )
    response.set_cookie(
        "refresh_token",
        tokens.refresh_token,
        httponly=True,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=settings.jwt_refresh_token_expire_days * 24 * 60 * 60,
        path="/",
        domain=settings.cookie_domain,
    )
    response.set_cookie(
        "csrf_token",
        csrf_token,
        httponly=False,
        secure=settings.cookie_secure,
        samesite=settings.cookie_samesite,
        max_age=settings.jwt_refresh_token_expire_days * 24 * 60 * 60,
        path="/",
        domain=settings.cookie_domain,
    )
    return csrf_token


def clear_auth_cookies(response: Response) -> None:
    for name in ("access_token", "refresh_token", "csrf_token"):
        response.delete_cookie(name, path="/", domain=settings.cookie_domain)
