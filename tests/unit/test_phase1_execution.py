"""
Phase 1 Execution Test

Validates full execution flow:

OrchestratorService
    → PlannerAgent
    → ExecutionService
    → SingleAgentExecutor
    → AgentService
    → ExecutionResult

No persistence required.
"""

import pytest

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
from app.schemas.execution import ExecutionResult

from app.services.orchestrator import OrchestratorService
from app.services.execution.execution_service import ExecutionService
from app.services.planner_agent import PlannerAgent
from app.services.agent_service import AgentService


# ==========================================================
# Stub TaskService (not used in execute(), but required by constructor)
# ==========================================================

class DummyTaskService:
    def create(self, task_in, execution_result):
        return None


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
def execution_service(agent_service):
    return ExecutionService(agent_service=agent_service)


@pytest.fixture
def orchestrator(agent_service, planner_agent, execution_service):
    return OrchestratorService(
        task_service=DummyTaskService(),
        agent_service=agent_service,
        planner_agent=planner_agent,
        execution_service=execution_service,
    )


# ==========================================================
# Test: Single Agent Execution
# ==========================================================

def test_single_agent_execution(orchestrator):
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

    result = orchestrator.execute(
        agent=agent,
        task_in=task,
    )

    # ======================================================
    # Assertions
    # ======================================================

    assert isinstance(result, ExecutionResult)

    assert result.status == "success"

    assert result.output is not None

    assert "EchoAgent" in result.output

    assert "hello world" in result.output.lower()