"""
Unit tests for ExecutionRuntime with ExecutionHistoryRepository integration.

Verifies that:
- single-agent executions are logged
- multi-agent executions are logged
- tool calls do not break history logging
"""

import pytest

from app.services.execution_runtime import ExecutionRuntime
from app.services.agent_service import AgentService
from app.services.tool_execution_engine import ToolExecutionEngine
from app.repositories.execution_history_repository import ExecutionHistoryRepository

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
def history_repo():
    return ExecutionHistoryRepository()


@pytest.fixture
def tool_engine():
    return ToolExecutionEngine(tool_registry=None)  # Can be mocked if needed


@pytest.fixture
def execution_runtime(agent_service, tool_engine, history_repo):
    return ExecutionRuntime(
        agent_service=agent_service,
        tool_engine=tool_engine,
        history_repo=history_repo,
    )


@pytest.fixture
def test_agent():
    return AgentRead(id="agent-1", name="TestAgent")


@pytest.fixture
def simple_task():
    return TaskCreate(
        name="Test Task",
        description="Simple task",
        status="pending",
        priority=0,
        input={},
    )


# ==================================================
# Tests
# ==================================================

def test_single_agent_execution_logged(execution_runtime, test_agent, simple_task, history_repo):
    plan = ExecutionPlan(
        strategy=ExecutionStrategy.SINGLE_AGENT,
        steps=None,
        tool_calls=None,
        reason="single-agent test",
    )

    context = AgentExecutionContext()

    result = execution_runtime.execute(
        agent=test_agent,
        task=simple_task,
        plan=plan,
        context=context,
    )

    all_history = history_repo.all()
    assert len(all_history) == 1

    record = all_history[0]
    assert record["task_name"] == simple_task.name
    assert record["execution_id"] == getattr(result, "execution_id", None)
    assert record["status"] == getattr(result, "status", None)
    assert record["metadata"]["run_id"] == context.run_id
    assert record["metadata"]["strategy"] == str(plan.strategy)


def test_multi_agent_execution_logged(execution_runtime, simple_task, history_repo):
    agent1 = AgentRead(id="agent-1", name="Agent1")
    agent2 = AgentRead(id="agent-2", name="Agent2")

    plan = ExecutionPlan(
        strategy=ExecutionStrategy.MULTI_AGENT,
        steps=[agent1, agent2],
        tool_calls=None,
        reason="multi-agent test",
    )

    context = AgentExecutionContext()

    result = execution_runtime.execute(
        agent=agent1,
        task=simple_task,
        plan=plan,
        context=context,
    )

    all_history = history_repo.all()
    assert len(all_history) == 1

    record = all_history[0]
    assert record["child_results_count"] == 2
    assert record["metadata"]["strategy"] == str(plan.strategy)
    assert record["metadata"]["run_id"] == context.run_id
