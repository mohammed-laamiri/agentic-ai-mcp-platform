"""
Central logging configuration for Phase 4.2 observability.

- Uses ContextVar to store correlation ID per request.
- Adds a logging.Filter to inject correlation ID into every log line.
- Safe to call multiple times (idempotent).
"""

import logging
from contextvars import ContextVar

# Each request will get its own correlation_id
correlation_id_ctx: ContextVar[str] = ContextVar(
    "correlation_id", default="unknown"
)


class CorrelationIdFilter(logging.Filter):
    """
    Logging filter to inject correlation ID into every log record.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        record.correlation_id = correlation_id_ctx.get()
        return True


def configure_logging() -> None:
    """
    Configure root logger with correlation ID filter and formatter.

    Safe to call multiple times.
    """
    logger = logging.getLogger()

    # If handlers already exist, assume logging is configured
    if logger.handlers:
        return

    handler = logging.StreamHandler()

    formatter = logging.Formatter(
        "[%(asctime)s] "
        "[%(levelname)s] "
        "[corr=%(correlation_id)s] "
        "%(name)s: %(message)s"
    )
    handler.setFormatter(formatter)
    handler.addFilter(CorrelationIdFilter())

    logger.addHandler(handler)
    logger.setLevel(logging.INFO)