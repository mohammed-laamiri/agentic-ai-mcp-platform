# tests/unit/test_planner_executor.py

import pytest

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
from app.schemas.agent_execution_context import AgentExecutionContext
from app.schemas.execution_strategy import ExecutionStrategy
from app.services.planner_agent import PlannerAgent


# ------------------------------
# Fixtures
# ------------------------------

@pytest.fixture
def planner_agent():
    return PlannerAgent(rag_service=None)


@pytest.fixture
def lead_agent():
    return AgentRead(id="agent_1", name="LeadAgent")


@pytest.fixture
def simple_task():
    return TaskCreate(name="Simple Task", description="Say hello")


@pytest.fixture
def complex_task():
    return TaskCreate(name="Complex Task", description="Analyze and summarize report data")


# ------------------------------
# Tests
# ------------------------------

def test_single_agent_execution(planner_agent, lead_agent, simple_task):
    """
    Simple task should result in SINGLE_AGENT strategy.
    """
    context = AgentExecutionContext()
    plan = planner_agent.plan_sync(
        agent=lead_agent,
        task=simple_task,
        context=context,
    )

    assert plan.strategy == ExecutionStrategy.SINGLE_AGENT
    assert plan.reason is not None
    assert "simple" in plan.reason.lower()


def test_multi_agent_execution(planner_agent, lead_agent, complex_task):
    """
    Complex task should result in MULTI_AGENT strategy.
    """
    context = AgentExecutionContext()
    plan = planner_agent.plan_sync(
        agent=lead_agent,
        task=complex_task,
        context=context,
    )

    assert plan.strategy == ExecutionStrategy.MULTI_AGENT
    assert plan.steps is not None
    assert len(plan.steps) >= 2
    assert plan.reason is not None
    assert "complex" in plan.reason.lower()
