"""
Unit tests for MultiAgentExecutor.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
from app.schemas.execution import ExecutionResult
from app.schemas.agent_execution_context import AgentExecutionContext
from app.services.execution.multi_agent_executor import MultiAgentExecutor


@pytest.fixture
def agents():
    return [
        AgentRead(id="agent-1", name="Agent1"),
        AgentRead(id="agent-2", name="Agent2"),
    ]


@pytest.fixture
def task():
    return TaskCreate(name="Test Task", description="Test description")


@pytest.fixture
def context():
    return AgentExecutionContext()


@pytest.fixture
def mock_agent_service():
    """Create a mock agent service with async execute."""
    service = MagicMock()
    service.execute = AsyncMock(return_value={
        "execution_id": "exec-1",
        "agent_id": "agent-1",
        "agent_name": "TestAgent",
        "input": "Test",
        "output": "Agent output",
        "status": "success",  # Lowercase to match our convention
    })
    return service


async def test_execute_sequential_agents(mock_agent_service, agents, task, context):
    """execute should run agents sequentially."""
    executor = MultiAgentExecutor(agent_service=mock_agent_service)

    result = await executor.execute(agents=agents, task_in=task, context=context)

    assert isinstance(result, ExecutionResult)
    assert result.status == "success"
    # Should be called twice for 2 agents
    assert mock_agent_service.execute.call_count == 2


async def test_execute_empty_agents(mock_agent_service, task, context):
    """execute with empty agents list should succeed."""
    executor = MultiAgentExecutor(agent_service=mock_agent_service)

    result = await executor.execute(agents=[], task_in=task, context=context)

    assert result.status == "success"
    assert result.output is None
    mock_agent_service.execute.assert_not_called()


async def test_execute_stops_on_error(task, context):
    """execute should stop and return on first error."""
    service = MagicMock()
    service.execute = AsyncMock(return_value={
        "execution_id": "exec-1",
        "status": "error",
        "output": None,
        "error": "Agent failed",
    })
    executor = MultiAgentExecutor(agent_service=service)

    agents = [
        AgentRead(id="agent-1", name="Agent1"),
        AgentRead(id="agent-2", name="Agent2"),
    ]

    result = await executor.execute(agents=agents, task_in=task, context=context)

    assert result.status == "error"
    # Should stop after first agent fails
    assert service.execute.call_count == 1


async def test_execute_updates_context_metadata(mock_agent_service, agents, task, context):
    """execute should update context metadata with last output."""
    executor = MultiAgentExecutor(agent_service=mock_agent_service)

    await executor.execute(agents=agents, task_in=task, context=context)

    assert "last_output" in context.metadata
    assert context.metadata["last_output"] == "Agent output"


async def test_execute_handles_execution_result_return(agents, task, context):
    """execute should handle ExecutionResult returned directly."""
    service = MagicMock()
    service.execute = AsyncMock(return_value=ExecutionResult(
        execution_id="exec-1",
        status="success",
        output="Direct result",
    ))
    executor = MultiAgentExecutor(agent_service=service)

    result = await executor.execute(agents=agents, task_in=task, context=context)

    assert result.status == "success"


async def test_execute_handles_exception(agents, task, context):
    """execute should catch exceptions and return error result."""
    service = MagicMock()
    service.execute = AsyncMock(side_effect=RuntimeError("Agent crashed"))
    executor = MultiAgentExecutor(agent_service=service)

    result = await executor.execute(agents=agents, task_in=task, context=context)

    assert result.status == "error"
    assert "Multi-agent execution failed" in result.error


async def test_execute_returns_last_output(task, context):
    """execute should return output from last agent."""
    call_count = 0

    async def mock_execute(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        return {
            "execution_id": f"exec-{call_count}",
            "status": "success",
            "output": f"Output from agent {call_count}",
        }

    service = MagicMock()
    service.execute = AsyncMock(side_effect=mock_execute)
    executor = MultiAgentExecutor(agent_service=service)

    agents = [
        AgentRead(id="agent-1", name="Agent1"),
        AgentRead(id="agent-2", name="Agent2"),
    ]

    result = await executor.execute(agents=agents, task_in=task, context=context)

    assert result.output == "Output from agent 2"


async def test_default_agent_service():
    """MultiAgentExecutor should create default AgentService if not provided."""
    executor = MultiAgentExecutor()

    assert executor._agent_service is not None


async def test_execute_multi_agent_stream_with_dict_result(task, context):
    """_execute_multi_agent_stream should yield agent events for dict results."""
    from app.schemas.execution_plan import ExecutionPlan
    from app.schemas.execution_strategy import ExecutionStrategy

    service = MagicMock()
    service.execute = AsyncMock(return_value={
        "execution_id": "exec-1",
        "status": "success",
        "output": "Agent output",
    })
    executor = MultiAgentExecutor(agent_service=service)

    agents = [
        AgentRead(id="agent-1", name="Agent1"),
        AgentRead(id="agent-2", name="Agent2"),
    ]
    plan = ExecutionPlan(strategy=ExecutionStrategy.MULTI_AGENT, steps=agents)

    events = []
    async for event in executor._execute_multi_agent_stream(task, plan, context):
        events.append(event)

    assert len(events) == 4  # 2 agent_start + 2 agent_result
    assert events[0]["type"] == "agent_start"
    assert events[0]["agent_id"] == "agent-1"
    assert events[1]["type"] == "agent_result"


async def test_execute_multi_agent_stream_with_execution_result(task, context):
    """_execute_multi_agent_stream should yield agent events for ExecutionResult."""
    from app.schemas.execution_plan import ExecutionPlan
    from app.schemas.execution_strategy import ExecutionStrategy

    service = MagicMock()
    service.execute = AsyncMock(return_value=ExecutionResult(
        execution_id="exec-1",
        status="success",
        output="ExecutionResult output",
    ))
    executor = MultiAgentExecutor(agent_service=service)

    agents = [AgentRead(id="agent-1", name="Agent1")]
    plan = ExecutionPlan(strategy=ExecutionStrategy.MULTI_AGENT, steps=agents)

    events = []
    async for event in executor._execute_multi_agent_stream(task, plan, context):
        events.append(event)

    assert len(events) == 2  # 1 agent_start + 1 agent_result
    assert events[0]["type"] == "agent_start"
    assert events[1]["type"] == "agent_result"
    assert events[1]["data"]["output"] == "ExecutionResult output"


async def test_execute_multi_agent_stream_empty_steps(task, context):
    """_execute_multi_agent_stream should handle empty steps."""
    from app.schemas.execution_plan import ExecutionPlan
    from app.schemas.execution_strategy import ExecutionStrategy

    executor = MultiAgentExecutor()
    plan = ExecutionPlan(strategy=ExecutionStrategy.MULTI_AGENT, steps=[])

    events = []
    async for event in executor._execute_multi_agent_stream(task, plan, context):
        events.append(event)

    assert len(events) == 0
