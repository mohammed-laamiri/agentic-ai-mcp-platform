"""
Unit tests for ExecutionService.

Tests both execute_plan and stream_execute_plan methods.
"""

import pytest

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
from app.schemas.execution_plan import ExecutionPlan
from app.schemas.execution_strategy import ExecutionStrategy
from app.schemas.agent_execution_context import AgentExecutionContext
from app.schemas.execution_event import ExecutionEventType
from app.services.execution.execution_service import ExecutionService


@pytest.fixture
def execution_service():
    return ExecutionService()


@pytest.fixture
def agent():
    return AgentRead(id="agent-1", name="TestAgent")


@pytest.fixture
def task():
    return TaskCreate(name="Test Task", description="Test description")


@pytest.fixture
def context():
    return AgentExecutionContext()


@pytest.fixture
def single_agent_plan(agent):
    return ExecutionPlan(
        strategy=ExecutionStrategy.MULTI_AGENT,
        steps=[agent],
        reason="Test plan",
    )


@pytest.fixture
def multi_agent_plan(agent):
    return ExecutionPlan(
        strategy=ExecutionStrategy.MULTI_AGENT,
        steps=[agent, agent],
        reason="Multi-agent test plan",
    )


async def test_execute_plan_returns_execution_result(
    execution_service, agent, task, single_agent_plan, context
):
    """execute_plan should return ExecutionResult."""
    result = await execution_service.execute_plan(
        agent=agent,
        task_in=task,
        plan=single_agent_plan,
        context=context,
    )

    assert result is not None
    assert result.status == "success"
    assert result.output is not None


async def test_execute_plan_multi_agent(
    execution_service, agent, task, multi_agent_plan, context
):
    """execute_plan should handle multi-agent plans."""
    result = await execution_service.execute_plan(
        agent=agent,
        task_in=task,
        plan=multi_agent_plan,
        context=context,
    )

    assert result is not None
    assert result.status == "success"
    # Should have output from both agents
    assert "TestAgent" in result.output


async def test_stream_execute_plan_yields_events(
    execution_service, agent, task, single_agent_plan, context
):
    """stream_execute_plan should yield execution events."""
    events = []
    async for event in execution_service.stream_execute_plan(
        agent=agent,
        task=task,
        plan=single_agent_plan,
        context=context,
    ):
        events.append(event)

    # Check expected event types
    event_types = [e.type for e in events]
    assert ExecutionEventType.EXECUTION_STARTED in event_types
    assert ExecutionEventType.STEP_STARTED in event_types
    assert ExecutionEventType.TOKEN_CHUNK in event_types
    assert ExecutionEventType.STEP_COMPLETED in event_types
    assert ExecutionEventType.EXECUTION_COMPLETED in event_types


async def test_stream_execute_plan_token_chunks(
    execution_service, agent, task, single_agent_plan, context
):
    """stream_execute_plan should yield token chunks."""
    token_events = []
    async for event in execution_service.stream_execute_plan(
        agent=agent,
        task=task,
        plan=single_agent_plan,
        context=context,
    ):
        if event.type == ExecutionEventType.TOKEN_CHUNK:
            token_events.append(event)

    assert len(token_events) > 0
    # Each token event should have a token
    for event in token_events:
        assert event.token is not None


async def test_stream_execute_plan_step_events(
    execution_service, agent, task, multi_agent_plan, context
):
    """stream_execute_plan should yield step events for each agent."""
    step_started = []
    step_completed = []

    async for event in execution_service.stream_execute_plan(
        agent=agent,
        task=task,
        plan=multi_agent_plan,
        context=context,
    ):
        if event.type == ExecutionEventType.STEP_STARTED:
            step_started.append(event)
        elif event.type == ExecutionEventType.STEP_COMPLETED:
            step_completed.append(event)

    # Should have 2 steps (one per agent in plan)
    assert len(step_started) == 2
    assert len(step_completed) == 2


async def test_execute_plan_empty_steps():
    """execute_plan with empty steps should complete without errors."""
    service = ExecutionService()
    agent = AgentRead(id="agent-1", name="TestAgent")
    task = TaskCreate(name="Empty Task", description="No steps")
    plan = ExecutionPlan(
        strategy=ExecutionStrategy.MULTI_AGENT,
        steps=[],
        reason="Empty plan",
    )
    context = AgentExecutionContext()

    result = await service.execute_plan(
        agent=agent,
        task_in=task,
        plan=plan,
        context=context,
    )

    assert result is not None
    assert result.status == "success"
    assert result.output == ""


async def test_stream_execute_plan_handles_exception():
    """stream_execute_plan should yield EXECUTION_FAILED and re-raise on exception."""
    service = ExecutionService()
    agent = AgentRead(id="agent-1", name="TestAgent")
    task = TaskCreate(name="Failing Task", description="Will fail")
    context = AgentExecutionContext()

    # Create a list that raises on iteration
    class FailingList:
        def __iter__(self):
            raise RuntimeError("Failed to iterate steps")

    plan = ExecutionPlan(
        strategy=ExecutionStrategy.MULTI_AGENT,
        steps=[agent],
        reason="Test",
    )
    # Patch steps to use our failing list
    plan.steps = FailingList()

    events = []
    with pytest.raises(RuntimeError, match="Failed to iterate steps"):
        async for event in service.stream_execute_plan(
            agent=agent,
            task=task,
            plan=plan,
            context=context,
        ):
            events.append(event)

    # Should have EXECUTION_STARTED and then EXECUTION_FAILED
    event_types = [e.type for e in events]
    assert ExecutionEventType.EXECUTION_STARTED in event_types
    assert ExecutionEventType.EXECUTION_FAILED in event_types


async def test_execute_plan_with_none_context():
    """execute_plan should handle None context gracefully."""
    service = ExecutionService()
    agent = AgentRead(id="agent-1", name="TestAgent")
    task = TaskCreate(name="Task", description="Test")
    plan = ExecutionPlan(
        strategy=ExecutionStrategy.MULTI_AGENT,
        steps=[agent],
        reason="Test",
    )

    # Pass None context
    result = await service.execute_plan(
        agent=agent,
        task_in=task,
        plan=plan,
        context=None,
    )

    # Should still produce a result with fallback execution_id
    assert result is not None
    assert result.execution_id is not None
