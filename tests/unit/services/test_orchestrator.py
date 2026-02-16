"""
Unit tests for OrchestratorService.
"""

from app.services.orchestrator import OrchestratorService
from app.services.agent_service import AgentService
from app.services.task_service import TaskService
from app.services.tool_registry import ToolRegistry
from app.services.memory_writer import MemoryWriter
from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate


def test_orchestrator_run_happy_path(session):
    task_service = TaskService(session)
    agent_service = AgentService()
    tool_registry = ToolRegistry()
    memory_writer = MemoryWriter()

    orchestrator = OrchestratorService(
        task_service=task_service,
        agent_service=agent_service,
        tool_registry=tool_registry,
        memory_writer=memory_writer,
    )

    agent = AgentRead(id="agent-1", name="TestAgent")
    task = TaskCreate(description="Orchestrated task")

    result = orchestrator.run(agent=agent, task_in=task)

    assert result.description == "Orchestrated task"
    assert result.status == "completed"
    assert result.result is not None
