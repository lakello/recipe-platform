import logging
import secrets

from asgi_correlation_id import CorrelationIdMiddleware
from asgi_correlation_id.context import correlation_id
from pythonjsonlogger.json import JsonFormatter
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

logger = logging.getLogger(__name__)


class RequestIdJsonFormatter(JsonFormatter):
    def add_fields(
        self,
        log_record: dict[str, object],
        record: logging.LogRecord,
        message_dict: dict[str, object],
    ) -> None:
        super().add_fields(log_record, record, message_dict)
        log_record["request_id"] = correlation_id.get()


class CSRFMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        uses_bearer = (
            request.headers.get("authorization", "").lower().startswith("bearer ")
        )
        path = request.url.path
        ignores_auth_cookies = path in {
            "/api/auth/login",
            "/api/auth/register",
        } or path.startswith("/api/auth/token/")
        uses_cookie_auth = not ignores_auth_cookies and (
            bool(request.cookies.get("access_token"))
            or (
                request.url.path in {"/api/auth/refresh", "/api/auth/logout"}
                and bool(request.cookies.get("refresh_token"))
            )
        )
        if (
            request.method not in {"GET", "HEAD", "OPTIONS"}
            and uses_cookie_auth
            and not uses_bearer
        ):
            cookie_token = request.cookies.get("csrf_token", "")
            header_token = request.headers.get("x-csrf-token", "")
            if not cookie_token or not secrets.compare_digest(
                cookie_token, header_token
            ):
                return JSONResponse(
                    {"detail": "CSRF token missing or invalid"}, status_code=403
                )
        return await call_next(request)


__all__ = ["CSRFMiddleware", "CorrelationIdMiddleware", "RequestIdJsonFormatter"]
