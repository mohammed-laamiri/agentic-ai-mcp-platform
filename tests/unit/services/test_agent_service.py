"""
Unit tests for AgentService.

These tests validate deterministic execution behavior.
"""

from app.services.agent_service import AgentService
from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
from app.schemas.tool_call import ToolCall
from app.schemas.execution import ExecutionResult


def test_agent_execute_returns_stub_response():
    """execute_sync returns ExecutionResult with agent output."""
    service = AgentService()

    agent = AgentRead(id="agent-1", name="TestAgent")
    task = TaskCreate(name="Test Task", description="Test task")

    result = service.execute_sync(agent=agent, task=task)

    assert isinstance(result, ExecutionResult)
    assert result.status == "success"
    assert "agent-1" in result.output
    assert "AGENT EXECUTION" in result.output


def test_agent_execute_tool_returns_stub_result():
    """execute_tool returns a ToolResult."""
    service = AgentService()
    call = ToolCall(tool_id="search", arguments={"q": "test"})
    result = service.execute_tool(call)
    # When tool is not registered, ToolExecutor returns error (expected behavior)
    assert result.tool_id == "search"
    # The result indicates the tool is not found
    assert result.success is False or "not registered" in (result.error or "")
