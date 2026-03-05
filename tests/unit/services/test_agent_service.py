"""
Unit tests for AgentService.

These tests validate deterministic execution behavior
and standardized ExecutionResult contract.
"""

from app.services.agent_service import AgentService
from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
from app.schemas.execution import ExecutionResult


def test_agent_execute_returns_execution_result():
    service = AgentService()

    agent = AgentRead(id="agent-1", name="TestAgent")
    task = TaskCreate(description="Test task")

    result = service.execute(agent=agent, task=task)

    # Validate type
    assert isinstance(result, ExecutionResult)

    # Validate status
    assert result.status == "success"
    assert result.success is True

    # Validate output content
    assert "agent-1" in result.output
    assert "Test task" in result.output

    # Validate timestamps
    assert result.started_at is not None
    assert result.finished_at is not None