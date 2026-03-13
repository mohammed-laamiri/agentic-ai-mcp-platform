"""
Unit tests for API middleware.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.middleware.correlation import CorrelationIdMiddleware
from app.core.logging import correlation_id_ctx


def test_correlation_middleware_generates_id():
    """Middleware should generate correlation ID when not provided."""
    app = FastAPI()
    app.add_middleware(CorrelationIdMiddleware)

    @app.get("/test")
    def test_endpoint():
        return {"status": "ok"}

    client = TestClient(app)
    response = client.get("/test")

    assert response.status_code == 200
    assert "X-Correlation-ID" in response.headers
    # Should be a valid UUID format
    correlation_id = response.headers["X-Correlation-ID"]
    assert len(correlation_id) == 36  # UUID format


def test_correlation_middleware_uses_provided_id():
    """Middleware should use provided correlation ID."""
    app = FastAPI()
    app.add_middleware(CorrelationIdMiddleware)

    @app.get("/test")
    def test_endpoint():
        return {"status": "ok"}

    client = TestClient(app)
    custom_id = "custom-correlation-id-12345"
    response = client.get("/test", headers={"X-Correlation-ID": custom_id})

    assert response.status_code == 200
    assert response.headers["X-Correlation-ID"] == custom_id


def test_correlation_middleware_returns_id_in_response():
    """Middleware should return correlation ID in response headers."""
    app = FastAPI()
    app.add_middleware(CorrelationIdMiddleware)

    @app.get("/test")
    def test_endpoint():
        return {"status": "ok"}

    client = TestClient(app)
    response = client.get("/test")

    assert "X-Correlation-ID" in response.headers
    assert response.headers["X-Correlation-ID"] is not None
