"""
Unit tests for AgentExecutionContext.

Covers add_tool_result, tool_results property, and mark_completed.
"""

from app.schemas.agent_execution_context import AgentExecutionContext
from app.schemas.tool_call import ToolCall
from app.schemas.tool_result import ToolResult


def test_add_tool_result():
    """add_tool_result appends to tool_results."""
    ctx = AgentExecutionContext()
    r = ToolResult(tool_id="t", success=True, output="out")
    ctx.add_tool_result(r)
    assert len(ctx.tool_results) == 1
    assert ctx.tool_results[0].tool_id == "t"


def test_tool_results_property():
    """tool_results returns list of ToolResults."""
    ctx = AgentExecutionContext()
    assert ctx.tool_results == []
    ctx.add_tool_result(ToolResult(tool_id="a", success=True))
    ctx.add_tool_result(ToolResult(tool_id="b", success=False))
    assert len(ctx.tool_results) == 2


def test_mark_completed():
    """mark_completed sets status and finished_at."""
    ctx = AgentExecutionContext()
    ctx.mark_completed("completed")
    assert ctx.status == "completed"
    assert ctx.finished_at is not None
