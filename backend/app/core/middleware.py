import logging

from asgi_correlation_id import CorrelationIdMiddleware
from asgi_correlation_id.context import correlation_id
from pythonjsonlogger.json import JsonFormatter

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


__all__ = ["CorrelationIdMiddleware", "RequestIdJsonFormatter"]
