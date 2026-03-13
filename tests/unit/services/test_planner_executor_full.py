"""
Unit tests for PlannerExecutor.

Tests the plan_and_execute method that combines planning and execution.
"""

import pytest
from unittest.mock import MagicMock

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
from app.schemas.execution import ExecutionResult
from app.schemas.execution_plan import ExecutionPlan
from app.schemas.execution_strategy import ExecutionStrategy
from app.schemas.agent_execution_context import AgentExecutionContext
from app.services.planner_executor import PlannerExecutor
from app.services.planner_agent import PlannerAgent


@pytest.fixture
def agent():
    return AgentRead(id="agent-1", name="TestAgent")


@pytest.fixture
def simple_task():
    return TaskCreate(name="Simple Task", description="A simple task")


@pytest.fixture
def complex_task():
    return TaskCreate(name="Complex Task", description="Analyze and summarize data")


@pytest.fixture
def mock_execution_service():
    """Mock execution service that returns ExecutionResult."""
    service = MagicMock()
    service.execute_plan_sync = MagicMock(return_value=ExecutionResult(
        execution_id="exec-1",
        status="SUCCESS",
        output="Execution completed",
    ))
    return service


@pytest.fixture
def planner_agent():
    return PlannerAgent()


def test_plan_and_execute_simple_task(planner_agent, mock_execution_service, agent, simple_task):
    """plan_and_execute should work for simple tasks."""
    executor = PlannerExecutor(
        planner_agent=planner_agent,
        execution_service=mock_execution_service,
    )

    result = executor.plan_and_execute_sync(agent=agent, task=simple_task)

    assert isinstance(result, ExecutionResult)
    mock_execution_service.execute_plan_sync.assert_called_once()


def test_plan_and_execute_complex_task(planner_agent, mock_execution_service, agent, complex_task):
    """plan_and_execute should work for complex tasks."""
    executor = PlannerExecutor(
        planner_agent=planner_agent,
        execution_service=mock_execution_service,
    )

    result = executor.plan_and_execute_sync(agent=agent, task=complex_task)

    assert isinstance(result, ExecutionResult)


def test_plan_and_execute_creates_context_if_none(planner_agent, mock_execution_service, agent, simple_task):
    """plan_and_execute should create context if not provided."""
    executor = PlannerExecutor(
        planner_agent=planner_agent,
        execution_service=mock_execution_service,
    )

    result = executor.plan_and_execute_sync(agent=agent, task=simple_task, context=None)

    assert isinstance(result, ExecutionResult)


def test_plan_and_execute_uses_provided_context(planner_agent, mock_execution_service, agent, simple_task):
    """plan_and_execute should use provided context."""
    executor = PlannerExecutor(
        planner_agent=planner_agent,
        execution_service=mock_execution_service,
    )
    context = AgentExecutionContext()

    result = executor.plan_and_execute_sync(agent=agent, task=simple_task, context=context)

    assert isinstance(result, ExecutionResult)


def test_plan_and_execute_handles_dict_plan():
    """plan_and_execute should handle plan returned as dict."""
    planner = MagicMock()
    planner.plan_sync = MagicMock(return_value={
        "strategy": "single_agent",
        "steps": [],
        "reason": "Simple task",
    })

    execution_service = MagicMock()
    execution_service.execute_plan_sync = MagicMock(return_value=ExecutionResult(
        execution_id="exec-1",
        status="SUCCESS",
        output="Done",
    ))

    executor = PlannerExecutor(
        planner_agent=planner,
        execution_service=execution_service,
    )

    agent = AgentRead(id="agent-1", name="Agent")
    task = TaskCreate(name="Task", description="Test")

    result = executor.plan_and_execute_sync(agent=agent, task=task)

    assert isinstance(result, ExecutionResult)


def test_plan_and_execute_handles_dict_result():
    """plan_and_execute should handle result returned as dict."""
    planner = PlannerAgent()

    execution_service = MagicMock()
    execution_service.execute_plan_sync = MagicMock(return_value={
        "execution_id": "exec-1",
        "status": "SUCCESS",
        "output": "Done",
    })

    executor = PlannerExecutor(
        planner_agent=planner,
        execution_service=execution_service,
    )

    agent = AgentRead(id="agent-1", name="Agent")
    task = TaskCreate(name="Task", description="Test")

    result = executor.plan_and_execute_sync(agent=agent, task=task)

    assert isinstance(result, ExecutionResult)


def test_plan_and_execute_handles_invalid_result_type():
    """plan_and_execute should handle invalid result type gracefully."""
    planner = PlannerAgent()

    execution_service = MagicMock()
    execution_service.execute_plan_sync = MagicMock(return_value="invalid_string")

    executor = PlannerExecutor(
        planner_agent=planner,
        execution_service=execution_service,
    )

    agent = AgentRead(id="agent-1", name="Agent")
    task = TaskCreate(name="Task", description="Test")

    result = executor.plan_and_execute_sync(agent=agent, task=task)

    assert isinstance(result, ExecutionResult)
    assert result.status == "error"
    assert "invalid result type" in result.error.lower()


def test_plan_and_execute_attaches_plan_reason(planner_agent, mock_execution_service, agent, simple_task):
    """plan_and_execute should attach plan reason to result."""
    executor = PlannerExecutor(
        planner_agent=planner_agent,
        execution_service=mock_execution_service,
    )

    result = executor.plan_and_execute_sync(agent=agent, task=simple_task)

    # Result should have plan_reason attribute set
    assert hasattr(result, "plan_reason")
