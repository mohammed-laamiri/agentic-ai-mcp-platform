"""
Unit tests for ToolExecutor.

Covers registered tool execution, unregistered tool, custom tool_fn, and exception path.
"""

import pytest

from app.services.tool_executor import ToolExecutor
from app.services.tool_registry import ToolRegistry, ToolMetadata
from app.schemas.tool_call import ToolCall
from app.schemas.tool_result import ToolResult
from app.schemas.agent_execution_context import AgentExecutionContext


@pytest.fixture
def registry():
    r = ToolRegistry()
    r.register_tool(
        ToolMetadata(tool_id="add", name="Add", version="1.0", description="Add two numbers"),
        executor=lambda a, b: a + b,
    )
    return r


@pytest.fixture
def executor(registry):
    return ToolExecutor(tool_registry=registry)


def test_execute_unregistered_tool_returns_error_result(executor):
    """Executing an unregistered tool returns a failed ToolResult."""
    call = ToolCall(tool_id="nonexistent", arguments={})
    result = executor.execute(call)
    assert not result.success
    assert "not registered" in (result.error or "")


def test_execute_registered_tool_uses_stub_when_no_executor(registry):
    """When no executor is bound, a stub is used and returns success."""
    registry.register_tool(
        ToolMetadata(tool_id="stub-only", name="Stub", version="1.0", description="Stub"),
        executor=None,
    )
    exec_ = ToolExecutor(tool_registry=registry)
    call = ToolCall(tool_id="stub-only", arguments={"x": 1})
    result = exec_.execute(call)
    assert result.success
    assert "[STUB TOOL OUTPUT]" in (result.output or "")


def test_execute_with_custom_tool_fn(executor):
    """Passing tool_fn overrides stub and is called with tool_call.arguments (tool must be registered)."""
    call = ToolCall(tool_id="add", arguments={"a": 2, "b": 3})
    result = executor.execute(call, tool_fn=lambda a, b: a * b)
    assert result.success
    assert result.output == 6


def test_execute_when_tool_fn_raises_returns_failed_result(executor):
    """When tool_fn raises, ToolResult has success=False and error message (tool must be registered)."""
    call = ToolCall(tool_id="add", arguments={})

    def failing(**kwargs):
        raise ValueError("Tool failed")

    result = executor.execute(call, tool_fn=failing)
    assert not result.success
    assert result.error == "Tool failed"


def test_execute_attaches_run_id_when_context_provided(executor):
    """When context is provided, metadata includes run_id."""
    ctx = AgentExecutionContext(run_id="run-123")
    call = ToolCall(tool_id="add", arguments={"a": 1, "b": 2})
    result = executor.execute(call, context=ctx)
    assert result.success
    assert result.metadata.get("run_id") == "run-123"
