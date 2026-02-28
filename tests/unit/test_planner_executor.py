# tests/unit/test_planner_executor.py

import pytest

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
from app.schemas.agent_execution_context import AgentExecutionContext
from app.services.planner_agent import PlannerAgent
from app.services.planner_executor import PlannerExecutor
from app.services.execution.execution_service import ExecutionService
from app.services.agent_service import AgentService
from app.schemas.execution import ExecutionResult

# ------------------------------
# Fixtures
# ------------------------------

@pytest.fixture
def agent_service():
    return AgentService()  # Use a real or mocked AgentService

@pytest.fixture
def execution_service(agent_service):
    return ExecutionService(agent_service=agent_service)

@pytest.fixture
def planner_agent():
    return PlannerAgent(rag_service=None)

@pytest.fixture
def planner_executor(planner_agent, execution_service):
    return PlannerExecutor(
        planner_agent=planner_agent,
        execution_service=execution_service,
    )

@pytest.fixture
def lead_agent():
    return AgentRead(id="agent_1", name="LeadAgent")

@pytest.fixture
def simple_task():
    return TaskCreate(id="task_1", description="Say hello")

@pytest.fixture
def complex_task():
    return TaskCreate(id="task_2", description="Analyze and summarize report data")

# ------------------------------
# Tests
# ------------------------------

def test_single_agent_execution(planner_executor, lead_agent, simple_task):
    context = AgentExecutionContext(metadata={})
    result: ExecutionResult = planner_executor.plan_and_execute(
        agent=lead_agent,
        task=simple_task,
        context=context,
    )

    assert result.success
    assert "single_agent" == context.metadata.get("planning_strategy")
    assert hasattr(result, "plan_reason")
    assert "simple" in result.plan_reason.lower()

def test_multi_agent_execution(planner_executor, lead_agent, complex_task):
    context = AgentExecutionContext(metadata={})
    result: ExecutionResult = planner_executor.plan_and_execute(
        agent=lead_agent,
        task=complex_task,
        context=context,
    )

    assert result.success
    assert "multi_agent" == context.metadata.get("planning_strategy")
    assert hasattr(result, "plan_reason")
    assert "complex" in result.plan_reason.lower()