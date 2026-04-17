"""
Unit tests for logging module.

Tests correlation ID filter and logging configuration.
"""

import logging
import pytest

from app.core.logging import (
    correlation_id_ctx,
    CorrelationIdFilter,
    configure_logging,
)


def test_correlation_id_ctx_default():
    """correlation_id_ctx should have 'unknown' as default."""
    assert correlation_id_ctx.get() == "unknown"


def test_correlation_id_ctx_set_and_get():
    """correlation_id_ctx should store and retrieve values."""
    token = correlation_id_ctx.set("test-correlation-123")
    try:
        assert correlation_id_ctx.get() == "test-correlation-123"
    finally:
        correlation_id_ctx.reset(token)


def test_correlation_id_filter_adds_correlation_id():
    """CorrelationIdFilter should add correlation_id to log records."""
    filter_obj = CorrelationIdFilter()
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="test message",
        args=(),
        exc_info=None,
    )

    result = filter_obj.filter(record)

    assert result is True
    assert hasattr(record, "correlation_id")
    assert record.correlation_id == "unknown"


def test_correlation_id_filter_uses_context():
    """CorrelationIdFilter should use value from context."""
    token = correlation_id_ctx.set("custom-id-456")
    try:
        filter_obj = CorrelationIdFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="test message",
            args=(),
            exc_info=None,
        )

        filter_obj.filter(record)

        assert record.correlation_id == "custom-id-456"
    finally:
        correlation_id_ctx.reset(token)


def test_configure_logging_adds_handler():
    """configure_logging should add handler to root logger."""
    # Reset handlers for test
    logger = logging.getLogger()
    original_handlers = logger.handlers.copy()
    logger.handlers.clear()

    try:
        configure_logging()

        assert len(logger.handlers) > 0
        assert any(isinstance(h, logging.StreamHandler) for h in logger.handlers)
    finally:
        # Restore original handlers
        logger.handlers.clear()
        logger.handlers.extend(original_handlers)


def test_configure_logging_idempotent():
    """configure_logging should be idempotent."""
    # Reset handlers for test
    logger = logging.getLogger()
    original_handlers = logger.handlers.copy()
    logger.handlers.clear()

    try:
        configure_logging()
        handler_count_1 = len(logger.handlers)

        configure_logging()
        handler_count_2 = len(logger.handlers)

        assert handler_count_1 == handler_count_2
    finally:
        # Restore original handlers
        logger.handlers.clear()
        logger.handlers.extend(original_handlers)
