"""
Unit tests for AgentService.

These tests validate deterministic execution behavior.
"""

from app.services.agent_service import AgentService
from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
from app.schemas.tool_call import ToolCall


def test_agent_execute_returns_stub_response():
    service = AgentService()

    agent = AgentRead(id="agent-1", name="TestAgent")
    task = TaskCreate(name="Test Task", description="Test task")

    result = service.execute(agent=agent, task=task)

    assert result["agent_id"] == "agent-1"
    assert "STUB RESPONSE" in result["output"]
    assert "timestamp" in result


def test_agent_execute_tool_returns_stub_result():
    """execute_tool returns a stub ToolResult."""
    service = AgentService()
    call = ToolCall(tool_id="search", arguments={"q": "test"})
    result = service.execute_tool(call)
    assert result.success is True
    assert result.tool_id == "search"
    assert "STUB" in (result.output or "")
