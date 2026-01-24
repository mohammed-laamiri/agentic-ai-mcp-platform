"""
Unit tests for OrchestratorService.

Uses real services (no mocks yet).
"""

from app.services.orchestrator import OrchestratorService
from app.services.agent_service import AgentService
from app.services.task_service import TaskService
from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate


def test_orchestrator_run_happy_path():
    orchestrator = OrchestratorService(
        task_service=TaskService(),
        agent_service=AgentService(),
    )

    agent = AgentRead(id="agent-1", name="TestAgent")
    task = TaskCreate(description="Orchestrated task")

    result = orchestrator.run(agent=agent, task_in=task)

    assert result.description == "Orchestrated task"
    assert "STUB RESPONSE" in result.result
