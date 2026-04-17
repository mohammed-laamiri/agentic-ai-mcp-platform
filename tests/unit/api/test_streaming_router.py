"""
Unit tests for Streaming Router.

Tests SSE streaming endpoints.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.api.routers.streaming import router, _format_sse
from app.api.deps import get_orchestrator
from app.schemas.execution import ExecutionResult


@pytest.fixture
def mock_orchestrator():
    """Create a mock orchestrator."""
    orchestrator = MagicMock()
    orchestrator.execute = AsyncMock(return_value=ExecutionResult(
        execution_id="exec-1",
        status="SUCCESS",
        output="Streaming output",
    ))
    return orchestrator


@pytest.fixture
def app(mock_orchestrator):
    """Create test app with mocked dependencies."""
    app = FastAPI()
    app.dependency_overrides[get_orchestrator] = lambda: mock_orchestrator
    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


def test_format_sse():
    """_format_sse should format SSE message correctly."""
    result = _format_sse(
        event="status",
        data={"state": "starting"},
        event_id=1,
    )

    assert "id: 1" in result
    assert "event: status" in result
    assert "data:" in result
    assert "starting" in result


def test_stream_execution_success(client, mock_orchestrator):
    """stream_execution should return SSE stream on success."""
    response = client.post(
        "/execute/stream",
        json={
            "name": "Stream Task",
            "description": "Test streaming",
            "agent": {"id": "agent-1", "name": "TestAgent"},
        },
    )

    assert response.status_code == 200
    assert "text/event-stream" in response.headers["content-type"]


def test_stream_execution_with_error():
    """stream_execution should handle errors gracefully."""
    app = FastAPI()

    failing_orchestrator = MagicMock()
    failing_orchestrator.execute = AsyncMock(side_effect=RuntimeError("Execution error"))

    app.dependency_overrides[get_orchestrator] = lambda: failing_orchestrator
    app.include_router(router)

    client = TestClient(app)
    response = client.post(
        "/execute/stream",
        json={
            "name": "Failing Stream",
            "description": "Will fail",
            "agent": {"id": "agent-1", "name": "TestAgent"},
        },
    )

    # Should still return 200 as errors are in the stream
    assert response.status_code == 200
    # Error event should be in the response
    assert "error" in response.text


def test_stream_execution_contains_status_events(client):
    """stream_execution should contain status events."""
    response = client.post(
        "/execute/stream",
        json={
            "name": "Status Task",
            "description": "Check status events",
            "agent": {"id": "agent-1", "name": "TestAgent"},
        },
    )

    assert response.status_code == 200
    # Should have status events
    assert "status" in response.text
    # Should have starting state
    assert "starting" in response.text
