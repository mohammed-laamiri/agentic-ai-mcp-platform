"""
Unit tests for OrchestratorService.

Uses real services (no mocks yet).
"""

from app.services.orchestrator import Orchestrator
from app.services.agent_service import AgentService
from app.services.task_service import TaskService
from app.services.tool_registry import ToolRegistry
from app.services.memory_writer import MemoryWriter
from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate


def test_orchestrator_run_happy_path():
    orchestrator = Orchestrator(
        task_service=TaskService(),
        agent_service=AgentService(),
        tool_registry=ToolRegistry(),
        memory_writer=MemoryWriter(),
    )

    agent = AgentRead(id="agent-1", name="TestAgent")
    task = TaskCreate(description="Orchestrated task")

    result = orchestrator.run(agent=agent, task_in=task)

    assert result.description == "Orchestrated task"
    assert "STUB RESPONSE" in result.result
