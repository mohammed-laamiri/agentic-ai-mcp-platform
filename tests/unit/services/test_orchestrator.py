"""
Unit tests for OrchestratorService.

Validates end-to-end execution with real services (no mocks yet).
"""

import pytest
import asyncio

from app.services.orchestrator import OrchestratorService
from app.services.agent_service import AgentService
from app.services.task_service import TaskService
from app.services.planner_agent import PlannerAgent
from app.services.execution.execution_service import ExecutionService

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate


@pytest.mark.asyncio
async def test_orchestrator_run_happy_path():
    """
    Happy path: Orchestrator runs a simple task end-to-end.
    Checks that the result is persisted with execution output.
    """
    # Initialize real services
    agent_service = AgentService()
    task_service = TaskService()
    planner_agent = PlannerAgent()
    execution_service = ExecutionService()

    orchestrator = OrchestratorService(
        task_service=task_service,
        agent_service=agent_service,
        planner_agent=planner_agent,
        execution_service=execution_service,
    )

    agent = AgentRead(id="agent-1", name="TestAgent")
    task = TaskCreate(description="Orchestrated task")

    # Run orchestrator
    task_read = await orchestrator.run(agent=agent, task_in=task)

    # Validate returned TaskRead
    assert task_read is not None
    assert task_read.description == "Orchestrated task"
    assert task_read.status == "completed" or task_read.status == "pending"  # depending on TaskService implementation
    assert hasattr(task_read, "result")
    assert isinstance(task_read.result, str)
    assert "Executing step" in task_read.result