"""
Phase 1 Execution Test

Validates full execution flow:

OrchestratorService
    → PlannerAgent
    → AgentService
    → ExecutionResult

No persistence required.
"""

import pytest

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
from app.schemas.execution import ExecutionResult

from app.services.orchestrator import OrchestratorService
from app.services.planner_agent import PlannerAgent
from app.services.agent_service import AgentService
from app.services.task_service import TaskService
from app.services.tool_registry import ToolRegistry
from app.services.memory_writer import MemoryWriter


# ==========================================================
# Fixtures
# ==========================================================

@pytest.fixture
def agent_service():
    return AgentService()


@pytest.fixture
def planner_agent():
    return PlannerAgent()


@pytest.fixture
def tool_registry():
    return ToolRegistry()


@pytest.fixture
def memory_writer():
    return MemoryWriter()


@pytest.fixture
def orchestrator(agent_service, planner_agent, tool_registry, memory_writer):
    return OrchestratorService(
        task_service=TaskService(),
        agent_service=agent_service,
        planner_agent=planner_agent,
        tool_registry=tool_registry,
        memory_writer=memory_writer,
    )


# ==========================================================
# Test: Single Agent Execution
# ==========================================================

@pytest.mark.asyncio
async def test_single_agent_execution(orchestrator):
    """
    Validate that a simple task executes successfully
    through the full Phase 1 pipeline.
    """

    agent = AgentRead(
        id="agent-echo",
        name="EchoAgent",
    )

    task = TaskCreate(
        name="Test Task",
        description="Say hello world",
    )

    result = await orchestrator.execute(
        agent=agent,
        task_in=task,
    )

    # ======================================================
    # Assertions
    # ======================================================

    assert isinstance(result, ExecutionResult)

    assert result.status.lower() == "success"

    assert result.execution_id is not None
