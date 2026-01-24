"""
Unit tests for AgentService.

These tests validate deterministic execution behavior.
"""

from app.services.agent_service import AgentService
from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate


def test_agent_execute_returns_stub_response():
    service = AgentService()

    agent = AgentRead(id="agent-1", name="TestAgent")
    task = TaskCreate(description="Test task")

    result = service.execute(agent=agent, task=task)

    assert result["agent_id"] == "agent-1"
    assert "STUB RESPONSE" in result["output"]
    assert "timestamp" in result
