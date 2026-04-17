"""
Unit tests for SingleAgentExecutor.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
from app.schemas.execution import ExecutionResult
from app.schemas.agent_execution_context import AgentExecutionContext
from app.services.execution.single_agent_executor import SingleAgentExecutor


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
def mock_agent_service():
    """Create a mock agent service with async execute."""
    service = MagicMock()
    service.execute = AsyncMock(return_value={
        "execution_id": "exec-1",
        "agent_id": "agent-1",
        "agent_name": "TestAgent",
        "input": "Test",
        "output": "Test output",
        "status": "SUCCESS",
    })
    return service


async def test_execute_returns_execution_result(mock_agent_service, agent, task, context):
    """execute should return ExecutionResult."""
    executor = SingleAgentExecutor(agent_service=mock_agent_service)

    result = await executor.execute(agent=agent, task_in=task, context=context)

    assert isinstance(result, ExecutionResult)
    assert result.status == "SUCCESS"
    mock_agent_service.execute.assert_called_once()


async def test_execute_with_execution_result_return(agent, task, context):
    """execute should handle ExecutionResult returned directly."""
    service = MagicMock()
    service.execute = AsyncMock(return_value=ExecutionResult(
        execution_id="exec-1",
        status="SUCCESS",
        output="Direct result",
    ))
    executor = SingleAgentExecutor(agent_service=service)

    result = await executor.execute(agent=agent, task_in=task, context=context)

    assert isinstance(result, ExecutionResult)
    assert result.output == "Direct result"


async def test_execute_raises_on_none_agent(mock_agent_service, task, context):
    """execute should raise ValueError if agent is None."""
    executor = SingleAgentExecutor(agent_service=mock_agent_service)

    with pytest.raises(ValueError) as exc_info:
        await executor.execute(agent=None, task_in=task, context=context)

    assert "must all be provided" in str(exc_info.value)


async def test_execute_raises_on_none_task(mock_agent_service, agent, context):
    """execute should raise ValueError if task is None."""
    executor = SingleAgentExecutor(agent_service=mock_agent_service)

    with pytest.raises(ValueError) as exc_info:
        await executor.execute(agent=agent, task_in=None, context=context)

    assert "must all be provided" in str(exc_info.value)


async def test_execute_raises_on_none_context(mock_agent_service, agent, task):
    """execute should raise ValueError if context is None."""
    executor = SingleAgentExecutor(agent_service=mock_agent_service)

    with pytest.raises(ValueError) as exc_info:
        await executor.execute(agent=agent, task_in=task, context=None)

    assert "must all be provided" in str(exc_info.value)


async def test_execute_raises_on_invalid_return_type(agent, task, context):
    """execute should raise TypeError for invalid return type."""
    service = MagicMock()
    service.execute = AsyncMock(return_value="invalid_string")
    executor = SingleAgentExecutor(agent_service=service)

    with pytest.raises(TypeError) as exc_info:
        await executor.execute(agent=agent, task_in=task, context=context)

    assert "must return ExecutionResult or dict" in str(exc_info.value)


async def test_execute_single_agent_stream_dict_result(mock_agent_service, agent, task, context):
    """_execute_single_agent_stream should yield dict result."""
    executor = SingleAgentExecutor(agent_service=mock_agent_service)

    results = []
    async for event in executor._execute_single_agent_stream(agent, task, context):
        results.append(event)

    assert len(results) == 1
    assert results[0]["type"] == "result"
    assert "data" in results[0]


async def test_execute_single_agent_stream_execution_result(agent, task, context):
    """_execute_single_agent_stream should yield ExecutionResult as dict."""
    service = MagicMock()
    service.execute = AsyncMock(return_value=ExecutionResult(
        execution_id="exec-1",
        status="SUCCESS",
        output="Stream result",
    ))
    executor = SingleAgentExecutor(agent_service=service)

    results = []
    async for event in executor._execute_single_agent_stream(agent, task, context):
        results.append(event)

    assert len(results) == 1
    assert results[0]["type"] == "result"
    assert results[0]["data"]["output"] == "Stream result"


async def test_execute_single_agent_stream_async_iterator(agent, task, context):
    """_execute_single_agent_stream should handle async iterator results."""

    async def async_token_gen():
        for token in ["Hello", " ", "World"]:
            yield token

    service = MagicMock()
    service.execute = AsyncMock(return_value=async_token_gen())
    executor = SingleAgentExecutor(agent_service=service)

    results = []
    async for event in executor._execute_single_agent_stream(agent, task, context):
        results.append(event)

    assert len(results) == 3
    assert all(r["type"] == "token" for r in results)
    assert results[0]["content"] == "Hello"
    assert results[2]["content"] == "World"
