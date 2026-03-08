"""
Integration test fixtures for Agentic AI MCP Platform.

Handles the module-level singleton issue in Task/Agent routers
by clearing the actual singletons before/after each test.
"""

import sys
import pytest
from fastapi.testclient import TestClient

from app.main import app as fastapi_app
from app.api.deps import get_tool_registry
from app.services.tool_registry import ToolRegistry

# Import the routers package to ensure modules are loaded
import app.api.routers

# Access the actual modules via sys.modules (not the __init__.py exports)
task_router_mod = sys.modules["app.api.routers.task_router"]
agent_router_mod = sys.modules["app.api.routers.agent_router"]


@pytest.fixture(autouse=True)
def clean_state():
    """
    Clear router singletons before and after each test.

    CRITICAL: Access the actual module-level singletons, not new instances.
    - task_router_mod.task_service is the singleton used by /api/tasks endpoints
    - agent_router_mod.task_service is the singleton used by /api/agents endpoints
    """
    # Setup: clear before test
    task_router_mod.task_service._tasks.clear()
    agent_router_mod.task_service._tasks.clear()

    yield

    # Teardown: clear after test
    task_router_mod.task_service._tasks.clear()
    agent_router_mod.task_service._tasks.clear()


@pytest.fixture
def client():
    """
    Provide a TestClient with isolated tool_registry.

    The tool_router uses proper dependency injection, so we override
    get_tool_registry to provide a fresh registry per test.
    """
    test_registry = ToolRegistry()
    fastapi_app.dependency_overrides[get_tool_registry] = lambda: test_registry

    with TestClient(fastapi_app) as c:
        yield c

    fastapi_app.dependency_overrides.clear()


@pytest.fixture
def task_service_singleton():
    """Direct access to task router's singleton for state verification."""
    return task_router_mod.task_service


@pytest.fixture
def agent_service_singleton():
    """Direct access to agent router's singleton for state verification."""
    return agent_router_mod.task_service


@pytest.fixture
def tool_registry(client):
    """
    Access the test tool_registry that was injected into the client.

    Note: Must be used with client fixture to ensure override is active.
    """
    return fastapi_app.dependency_overrides[get_tool_registry]()
