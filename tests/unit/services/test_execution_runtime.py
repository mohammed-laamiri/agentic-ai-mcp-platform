"""
Unit tests for ExecutionRuntime.

Ensures execution runtime correctly executes:
- single agent plans
- multi-agent plans
- tool call propagation
"""

import pytest

from app.services.execution_runtime import ExecutionRuntime
from app.services.agent_service import AgentService
from app.services.tool_execution_engine import ToolExecutionEngine
from app.services.tool_registry import ToolRegistry

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
from app.schemas.execution_plan import ExecutionPlan
from app.schemas.execution_strategy import ExecutionStrategy
from app.schemas.agent_execution_context import AgentExecutionContext


# ==================================================
# Fixtures
# ==================================================

@pytest.fixture
def agent_service():
    return AgentService()


@pytest.fixture
def tool_registry():
    return ToolRegistry()


@pytest.fixture
def tool_engine(tool_registry):
    return ToolExecutionEngine(tool_registry=tool_registry)


@pytest.fixture
def execution_runtime(agent_service, tool_engine):
    return ExecutionRuntime(
        agent_service=agent_service,
        tool_engine=tool_engine,
    )


@pytest.fixture
def test_agent():
    return AgentRead(
        id="agent-test",
        name="TestAgent",
    )


@pytest.fixture
def simple_task():
    return TaskCreate(
        name="Test Task",
        description="Simple test execution",
        status="pending",
        priority=0,
        input={},
    )


# ==================================================
# Tests
# ==================================================

def test_execute_single_agent(
    execution_runtime,
    test_agent,
    simple_task,
):
    """
    Ensures single-agent execution works correctly.
    """

    plan = ExecutionPlan(
        strategy=ExecutionStrategy.SINGLE_AGENT,
        steps=None,
        tool_calls=None,
        reason="simple task",
    )

    context = AgentExecutionContext()

    result = execution_runtime.execute(
        agent=test_agent,
        task=simple_task,
        plan=plan,
        context=context,
    )

    assert result is not None
    assert result.status is not None
    assert context.run_id is not None


def test_execute_multi_agent(
    execution_runtime,
    simple_task,
):
    """
    Ensures multi-agent execution produces child results.
    """

    agent1 = AgentRead(id="agent-1", name="Agent1")
    agent2 = AgentRead(id="agent-2", name="Agent2")

    plan = ExecutionPlan(
        strategy=ExecutionStrategy.MULTI_AGENT,
        steps=[agent1, agent2],
        tool_calls=None,
        reason="multi agent test",
    )

    context = AgentExecutionContext()

    result = execution_runtime.execute(
        agent=agent1,
        task=simple_task,
        plan=plan,
        context=context,
    )

    assert result is not None
    assert result.child_results is not None
    assert len(result.child_results) == 2


def test_execution_runtime_propagates_tool_calls(
    execution_runtime,
    test_agent,
    simple_task,
):
    """
    Ensures tool calls collected in context do not break execution.
    """

    plan = ExecutionPlan(
        strategy=ExecutionStrategy.SINGLE_AGENT,
        steps=None,
        tool_calls=None,
        reason="tool propagation test",
    )

    context = AgentExecutionContext()

    result = execution_runtime.execute(
        agent=test_agent,
        task=simple_task,
        plan=plan,
        context=context,
    )

    assert result is not None
    assert isinstance(context.tool_calls, list)
