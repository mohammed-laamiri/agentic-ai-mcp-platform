"""
Unit tests for ToolExecutionEngine.

Covers hooks, execute_batch, fail_fast, and pre/post hook application.
"""

import pytest

from app.services.tool_execution_engine import ToolExecutionEngine
from app.services.tool_registry import ToolRegistry, ToolMetadata
from app.schemas.tool_call import ToolCall
from app.schemas.tool_result import ToolResult
from app.schemas.agent_execution_context import AgentExecutionContext


@pytest.fixture
def registry_with_tool():
    reg = ToolRegistry()
    reg.register_tool(
        ToolMetadata(
            tool_id="echo",
            name="Echo",
            version="1.0",
            description="Echoes input",
        ),
        executor=lambda **kwargs: str(kwargs),
    )
    return reg


@pytest.fixture
def engine(registry_with_tool):
    return ToolExecutionEngine(tool_registry=registry_with_tool)


@pytest.fixture
def context():
    return AgentExecutionContext()


def test_register_pre_hook(engine, context):
    """Pre-hooks are called before each tool execution."""
    seen = []

    def pre_hook(call: ToolCall, ctx: AgentExecutionContext) -> None:
        seen.append(("pre", call.tool_id))

    engine.register_pre_hook(pre_hook)
    call = ToolCall(tool_id="echo", arguments={"x": 1})
    engine.execute_batch(tool_calls=[call], context=context)
    assert len(seen) == 1
    assert seen[0] == ("pre", "echo")


def test_register_post_hook(engine, context):
    """Post-hooks are called after each tool execution."""
    seen = []

    def post_hook(result: ToolResult, ctx: AgentExecutionContext) -> None:
        seen.append(("post", result.tool_id))

    engine.register_post_hook(post_hook)
    call = ToolCall(tool_id="echo", arguments={})
    engine.execute_batch(tool_calls=[call], context=context)
    assert len(seen) == 1
    assert seen[0] == ("post", "echo")


def test_execute_batch_appends_results_to_context(engine, context):
    """execute_batch adds each ToolResult to context."""
    call = ToolCall(tool_id="echo", arguments={"a": 1})
    results = engine.execute_batch(tool_calls=[call], context=context)
    assert len(results) == 1
    assert results[0].success
    assert len(context.tool_results) == 1
    assert context.tool_results[0].tool_id == "echo"


def test_execute_batch_fail_fast_stops_on_failure(registry_with_tool, context):
    """When fail_fast=True, execution stops after first failure."""
    engine = ToolExecutionEngine(tool_registry=registry_with_tool)
    # First call: unregistered tool -> fails. Second: would run if not fail_fast.
    calls = [
        ToolCall(tool_id="nonexistent", arguments={}),
        ToolCall(tool_id="echo", arguments={}),
    ]
    results = engine.execute_batch(tool_calls=calls, context=context, fail_fast=True)
    assert len(results) == 1
    assert not results[0].success


def test_execute_batch_continue_on_error_when_not_fail_fast(registry_with_tool, context):
    """When fail_fast=False, all calls are executed."""
    engine = ToolExecutionEngine(tool_registry=registry_with_tool)
    reg = registry_with_tool
    reg.register_tool(
        ToolMetadata(tool_id="other", name="Other", version="1.0", description="Other"),
    )
    calls = [
        ToolCall(tool_id="nonexistent", arguments={}),
        ToolCall(tool_id="echo", arguments={}),
    ]
    results = engine.execute_batch(tool_calls=calls, context=context, fail_fast=False)
    assert len(results) == 2
    assert not results[0].success
    assert results[1].success
