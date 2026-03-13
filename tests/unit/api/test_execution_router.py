"""
Unit tests for Execution Router.

Tests execution endpoints with mocked dependencies.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.api.routers.execution_router import router, get_orchestrator
from app.api.dependencies.auth import require_api_key
from app.schemas.execution import ExecutionResult
from app.schemas.execution_event import ExecutionEvent, ExecutionEventType


@pytest.fixture
def mock_orchestrator():
    """Create a mock orchestrator."""
    orchestrator = MagicMock()
    orchestrator.execute = AsyncMock(return_value=ExecutionResult(
        execution_id="exec-1",
        status="SUCCESS",
        output="Test output",
    ))
    return orchestrator


@pytest.fixture
def app(mock_orchestrator):
    """Create test app with mocked dependencies."""
    app = FastAPI()

    # Override dependencies
    app.dependency_overrides[get_orchestrator] = lambda: mock_orchestrator
    app.dependency_overrides[require_api_key] = lambda: "test-key"

    app.include_router(router)
    return app


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


def test_execute_task_success(client, mock_orchestrator):
    """execute_task should return ExecutionResult on success."""
    response = client.post(
        "/execution/run",
        json={"name": "Test Task", "description": "Test description"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["execution_id"] == "exec-1"
    assert data["status"] == "SUCCESS"


def test_execute_task_with_error(client):
    """execute_task should return 500 on execution failure."""
    # Create app with failing orchestrator
    app = FastAPI()
    failing_orchestrator = MagicMock()
    failing_orchestrator.execute = AsyncMock(side_effect=RuntimeError("Execution failed"))

    app.dependency_overrides[get_orchestrator] = lambda: failing_orchestrator
    app.dependency_overrides[require_api_key] = lambda: "test-key"
    app.include_router(router)

    client = TestClient(app)
    response = client.post(
        "/execution/run",
        json={"name": "Failing Task", "description": "Will fail"},
    )

    assert response.status_code == 500
    assert "Execution failed" in response.json()["detail"]


def test_stream_execute_task_success():
    """stream_execute_task should return SSE stream."""
    app = FastAPI()

    # Mock orchestrator with async generator
    mock_orchestrator = MagicMock()

    async def mock_stream_execute(*args, **kwargs):
        yield ExecutionEvent(type=ExecutionEventType.EXECUTION_STARTED)
        yield ExecutionEvent(type=ExecutionEventType.EXECUTION_COMPLETED, output="Done")

    mock_orchestrator.stream_execute = mock_stream_execute

    app.dependency_overrides[get_orchestrator] = lambda: mock_orchestrator
    app.dependency_overrides[require_api_key] = lambda: "test-key"
    app.include_router(router)

    client = TestClient(app)
    response = client.post(
        "/execution/stream",
        json={"name": "Stream Task", "description": "Streaming"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"] == "text/event-stream; charset=utf-8"


def test_stream_execute_task_with_error():
    """stream_execute_task should handle errors in stream."""
    app = FastAPI()

    # Mock orchestrator that raises
    mock_orchestrator = MagicMock()

    async def mock_stream_execute(*args, **kwargs):
        yield ExecutionEvent(type=ExecutionEventType.EXECUTION_STARTED)
        raise RuntimeError("Stream error")

    mock_orchestrator.stream_execute = mock_stream_execute

    app.dependency_overrides[get_orchestrator] = lambda: mock_orchestrator
    app.dependency_overrides[require_api_key] = lambda: "test-key"
    app.include_router(router)

    client = TestClient(app)
    response = client.post(
        "/execution/stream",
        json={"name": "Failing Stream", "description": "Will fail"},
    )

    # Should still return 200 as errors are in the stream
    assert response.status_code == 200
