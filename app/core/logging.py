"""
Central logging configuration for Phase 4.2 observability.

- Uses ContextVar to store correlation ID per request.
- Adds a logging.Filter to inject correlation ID into every log line.
- Configurable for future structured logging or JSON output.
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

    This allows logs to automatically include the request context.
    """

    def filter(self, record):
        record.correlation_id = correlation_id_ctx.get()
        return True


def configure_logging():
    """
    Configure root logger with correlation ID filter and formatter.
    Call this once at FastAPI startup (main.py).
    """
    logger = logging.getLogger()

    # StreamHandler prints logs to console (stdout)
    handler = logging.StreamHandler()

    # Custom formatter including timestamp, level, correlation ID, and message
    formatter = logging.Formatter(
        "[%(asctime)s] "
        "[%(levelname)s] "
        "[corr=%(correlation_id)s] "
        "%(name)s: %(message)s"
    )
    handler.setFormatter(formatter)

    # Add correlation ID filter to every log record
    handler.addFilter(CorrelationIdFilter())

    # Add handler to root logger
    logger.addHandler(handler)

    # Set default log level (can be overridden by environment)
    logger.setLevel(logging.INFO)