from types import SimpleNamespace

import pytest
from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from app.api.auth import _limit_login
from app.api.oauth import _consume_state, _error_redirect
from app.core.auth_cookies import set_auth_cookies
from app.core.config import settings
from app.core.middleware import CSRFMiddleware
from app.core.rate_limit import enforce
from app.schemas.auth import LoginRequest, TokenResponse


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}
        self.counts: dict[str, int] = {}

    async def eval(self, script: str, keys: int, key: str, window: int) -> int:
        del script, keys, window
        self.counts[key] = self.counts.get(key, 0) + 1
        return self.counts[key]

    async def getdel(self, key: str) -> str | None:
        return self.values.pop(key, None)


@pytest.mark.asyncio
async def test_rate_limit_rejects_requests_over_limit() -> None:
    request = SimpleNamespace(
        app=SimpleNamespace(state=SimpleNamespace(redis=FakeRedis()))
    )
    await enforce(request, "login", "client", 1)  # type: ignore[arg-type]
    with pytest.raises(HTTPException) as exc:
        await enforce(request, "login", "client", 1)  # type: ignore[arg-type]
    assert exc.value.status_code == 429


@pytest.mark.asyncio
async def test_login_is_limited_by_ip_and_account() -> None:
    redis = FakeRedis()
    request = SimpleNamespace(
        headers={},
        client=SimpleNamespace(host="127.0.0.1"),
        app=SimpleNamespace(state=SimpleNamespace(redis=redis)),
    )
    await _limit_login(  # type: ignore[arg-type]
        request, LoginRequest(email="user@example.com", password="password")
    )
    assert len(redis.counts) == 2


@pytest.mark.asyncio
async def test_oauth_state_is_single_use() -> None:
    redis = FakeRedis()
    redis.values["oauth-state:state"] = "1"
    request = SimpleNamespace(
        cookies={"oauth_state": "state"},
        app=SimpleNamespace(state=SimpleNamespace(redis=redis)),
    )
    assert await _consume_state(request, "state") is True  # type: ignore[arg-type]
    assert await _consume_state(request, "state") is False  # type: ignore[arg-type]


def make_request(*headers: tuple[bytes, bytes]) -> Request:
    return Request(
        {
            "type": "http",
            "method": "POST",
            "path": "/change",
            "query_string": b"",
            "headers": list(headers),
            "scheme": "https",
            "server": ("test", 443),
            "client": ("127.0.0.1", 1234),
        }
    )


@pytest.mark.asyncio
async def test_cookie_auth_requires_matching_csrf_token() -> None:
    middleware = CSRFMiddleware(lambda scope, receive, send: None)

    async def endpoint(request: Request) -> JSONResponse:
        del request
        return JSONResponse({"ok": True})

    cookie = (b"cookie", b"access_token=access; csrf_token=csrf")
    rejected = await middleware.dispatch(make_request(cookie), endpoint)
    assert rejected.status_code == 403
    assert (
        await middleware.dispatch(
            make_request(cookie, (b"x-csrf-token", b"csrf")), endpoint
        )
    ).status_code == 200
    assert (
        await middleware.dispatch(
            make_request(cookie, (b"authorization", b"Bearer mobile-token")),
            endpoint,
        )
    ).status_code == 200


def test_auth_cookies_have_explicit_security_attributes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(settings, "cookie_secure", True)
    monkeypatch.setattr(settings, "cookie_samesite", "strict")
    monkeypatch.setattr(settings, "cookie_domain", "example.com")
    response = Response()
    set_auth_cookies(
        response,
        TokenResponse(access_token="access", refresh_token="refresh"),
    )
    cookies = response.headers.getlist("set-cookie")
    assert all(
        "Secure" in cookie
        and "SameSite=strict" in cookie
        and "Path=/" in cookie
        and "Domain=example.com" in cookie
        for cookie in cookies
    )
    assert "HttpOnly" in cookies[0] and "HttpOnly" in cookies[1]
    assert "HttpOnly" not in cookies[2]


def test_oauth_error_redirect_does_not_expose_internal_message() -> None:
    url = _error_redirect().headers["location"]
    assert "message=" not in url
    assert "oauth_error" in url
