"""
Unit tests for OrchestratorService.
"""

import pytest
from app.services.orchestrator import OrchestratorService
from app.services.agent_service import AgentService
from app.services.task_service import TaskService
from app.services.tool_registry import ToolRegistry
from app.services.memory_writer import MemoryWriter
from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate, TaskStatus


def test_orchestrator_run_happy_path():
    # -----------------------------
    # Setup services
    # -----------------------------
    task_service = TaskService()
    agent_service = AgentService()
    tool_registry = ToolRegistry()
    memory_writer = MemoryWriter()

    orchestrator = OrchestratorService(
        task_service=task_service,
        agent_service=agent_service,
        tool_registry=tool_registry,
        memory_writer=memory_writer,
    )

    # -----------------------------
    # Create test agent & task
    # -----------------------------
    agent = AgentRead(id="agent-1", name="TestAgent")

    task = TaskCreate(
        name="Orchestrated Task",         # REQUIRED
        description="Orchestrated task",  # optional
        status=TaskStatus.pending,        # REQUIRED
        priority=0,                        # default priority
        input={},                           # optional input dict
        project_id=None                     # optional project association
    )

    # -----------------------------
    # Run orchestrator
    # -----------------------------
    result = orchestrator.run(agent=agent, task_in=task)

    # -----------------------------
    # Assertions
    # -----------------------------
    assert result is not None
    assert result.name == "Orchestrated Task"
    assert result.description == "Orchestrated task"
    assert result.status == TaskStatus.pending  # TaskService does not change status on create
    assert result.id is not None
    assert isinstance(result.id, str)
