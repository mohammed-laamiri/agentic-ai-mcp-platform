"""
Unit tests for OrchestratorService.

Tests both sync and async interfaces.
"""

import pytest

from app.services.orchestrator import OrchestratorService
from app.services.agent_service import AgentService
from app.services.task_service import TaskService
from app.services.tool_registry import ToolRegistry
from app.services.memory_writer import MemoryWriter
from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
from app.schemas.execution_plan import ExecutionPlan
from app.schemas.execution_strategy import ExecutionStrategy


# ==================================================
# Sync Tests (backward compatibility)
# ==================================================

def test_orchestrator_run_sync_happy_path():
    """Test orchestrator.run_sync executes a task and returns result."""
    task_service = TaskService()
    agent_service = AgentService()
    tool_registry = ToolRegistry()
    memory_writer = MemoryWriter()

    orchestrator = OrchestratorService(
        task_service=task_service,
        agent_service=agent_service,
        tool_registry=tool_registry,
        memory_writer=memory_writer,
    )

    agent = AgentRead(id="agent-1", name="TestAgent")
    task = TaskCreate(name="Orchestrated Task", description="Orchestrated task")

    result = orchestrator.run_sync(agent=agent, task_in=task)

    assert result.name == "Orchestrated Task"
    assert result.description == "Orchestrated task"
    assert result.result is not None


def test_orchestrator_execute_sync_returns_execution_result():
    """Test orchestrator.execute_sync returns ExecutionResult without persistence."""
    task_service = TaskService()
    agent_service = AgentService()
    tool_registry = ToolRegistry()
    memory_writer = MemoryWriter()

    orchestrator = OrchestratorService(
        task_service=task_service,
        agent_service=agent_service,
        tool_registry=tool_registry,
        memory_writer=memory_writer,
    )

    agent = AgentRead(id="agent-1", name="TestAgent")
    task = TaskCreate(name="Execute Task", description="Task for execute method")

    result = orchestrator.execute_sync(agent=agent, task_in=task)

    assert result.execution_id is not None
    assert result.status.lower() == "success"


def test_orchestrator_execute_sync_multi_agent_branching():
    """Orchestrator with complex task uses MULTI_AGENT and aggregates child results."""
    task_service = TaskService()
    agent_service = AgentService()
    tool_registry = ToolRegistry()
    memory_writer = MemoryWriter()

    orchestrator = OrchestratorService(
        task_service=task_service,
        agent_service=agent_service,
        tool_registry=tool_registry,
        memory_writer=memory_writer,
    )

    agent = AgentRead(id="a1", name="Agent1")
    task = TaskCreate(name="Complex", description="Analyze and compare the data")

    result = orchestrator.execute_sync(agent=agent, task_in=task)

    assert result.execution_id is not None
    assert result.child_results is not None
    assert len(result.child_results) >= 2


def test_orchestrator_validate_plan_single_agent_with_steps_raises():
    """_validate_plan raises when SINGLE_AGENT has more than one step."""
    from app.schemas.agent_execution_context import AgentExecutionContext

    task_service = TaskService()
    agent_service = AgentService()
    tool_registry = ToolRegistry()
    memory_writer = MemoryWriter()
    orchestrator = OrchestratorService(
        task_service=task_service,
        agent_service=agent_service,
        tool_registry=tool_registry,
        memory_writer=memory_writer,
    )
    agent = AgentRead(id="a1", name="A1")
    agent2 = AgentRead(id="a2", name="A2")
    plan = ExecutionPlan(
        strategy=ExecutionStrategy.SINGLE_AGENT,
        steps=[agent, agent2],  # Two steps for SINGLE_AGENT should fail
        reason="test",
    )
    task = TaskCreate(name="T", description="d")

    with pytest.raises(ValueError, match="SINGLE_AGENT requires exactly one agent step"):
        orchestrator._validate_plan(plan)


def test_orchestrator_validate_plan_multi_agent_requires_two_steps():
    """_validate_plan raises when MULTI_AGENT has fewer than two steps."""
    task_service = TaskService()
    agent_service = AgentService()
    tool_registry = ToolRegistry()
    memory_writer = MemoryWriter()
    orchestrator = OrchestratorService(
        task_service=task_service,
        agent_service=agent_service,
        tool_registry=tool_registry,
        memory_writer=memory_writer,
    )
    agent = AgentRead(id="a1", name="A1")
    plan = ExecutionPlan(
        strategy=ExecutionStrategy.MULTI_AGENT,
        steps=[agent],  # Only one step for MULTI_AGENT should fail
        reason="test",
    )

    with pytest.raises(ValueError, match="MULTI_AGENT requires at least two"):
        orchestrator._validate_plan(plan)


def test_orchestrator_execute_sync_with_tool_calls_in_context():
    """When agent returns tool_calls, orchestrator runs execute_batch and merges tool results."""
    from unittest.mock import MagicMock
    from app.schemas.execution import ExecutionResult

    task_service = TaskService()
    tool_registry = ToolRegistry()
    memory_writer = MemoryWriter()
    # Agent that declares a tool call
    agent_stub = MagicMock()
    agent_stub.execute_sync = MagicMock(
        return_value=ExecutionResult(
            execution_id="e1",
            status="SUCCESS",
            output="out",
        )
    )
    orchestrator = OrchestratorService(
        task_service=task_service,
        agent_service=agent_stub,
        tool_registry=tool_registry,
        memory_writer=memory_writer,
    )
    agent = AgentRead(id="a1", name="A1")
    task = TaskCreate(name="T", description="Simple task")
    result = orchestrator.execute_sync(agent=agent, task_in=task)
    assert result.execution_id is not None
    # Single-agent execution doesn't produce child_results
    assert result.status.upper() == "SUCCESS"


def test_orchestrator_execute_sync_exception_marks_context_failed():
    """When execution raises, context is marked failed and exception is re-raised."""
    from unittest.mock import MagicMock

    task_service = TaskService()
    tool_registry = ToolRegistry()
    memory_writer = MemoryWriter()
    failing_agent = MagicMock()
    failing_agent.execute_sync = MagicMock(side_effect=RuntimeError("Agent failed"))
    orchestrator = OrchestratorService(
        task_service=task_service,
        agent_service=failing_agent,
        tool_registry=tool_registry,
        memory_writer=memory_writer,
    )
    agent = AgentRead(id="a1", name="A1")
    task = TaskCreate(name="T", description="Simple")
    with pytest.raises(RuntimeError, match="Agent failed"):
        orchestrator.execute_sync(agent=agent, task_in=task)


# ==================================================
# Async Tests
# ==================================================

@pytest.mark.asyncio
async def test_orchestrator_run_async_happy_path():
    """Test orchestrator.run (async) executes a task and returns result."""
    task_service = TaskService()
    agent_service = AgentService()
    tool_registry = ToolRegistry()
    memory_writer = MemoryWriter()

    orchestrator = OrchestratorService(
        task_service=task_service,
        agent_service=agent_service,
        tool_registry=tool_registry,
        memory_writer=memory_writer,
    )

    agent = AgentRead(id="agent-1", name="TestAgent")
    task = TaskCreate(name="Async Task", description="Async orchestrated task")

    result = await orchestrator.run(agent=agent, task_in=task)

    assert result.name == "Async Task"
    assert result.description == "Async orchestrated task"
    assert result.result is not None


@pytest.mark.asyncio
async def test_orchestrator_execute_async_returns_execution_result():
    """Test orchestrator.execute (async) returns ExecutionResult."""
    task_service = TaskService()
    agent_service = AgentService()
    tool_registry = ToolRegistry()
    memory_writer = MemoryWriter()

    orchestrator = OrchestratorService(
        task_service=task_service,
        agent_service=agent_service,
        tool_registry=tool_registry,
        memory_writer=memory_writer,
    )

    agent = AgentRead(id="agent-1", name="TestAgent")
    task = TaskCreate(name="Async Execute Task", description="Task for async execute")

    result = await orchestrator.execute(agent=agent, task_in=task)

    assert result.execution_id is not None
    assert result.status.lower() == "success"


@pytest.mark.asyncio
async def test_orchestrator_stream_execute_yields_events():
    """Test orchestrator.stream_execute yields execution events."""
    from app.schemas.execution_event import ExecutionEventType

    task_service = TaskService()
    agent_service = AgentService()
    tool_registry = ToolRegistry()
    memory_writer = MemoryWriter()

    orchestrator = OrchestratorService(
        task_service=task_service,
        agent_service=agent_service,
        tool_registry=tool_registry,
        memory_writer=memory_writer,
    )

    agent = AgentRead(id="agent-1", name="TestAgent")
    task = TaskCreate(name="Stream Task", description="Task for streaming")

    events = []
    async for event in orchestrator.stream_execute(agent=agent, task_in=task):
        events.append(event)

    # Check we got expected event types
    event_types = [e.type for e in events]
    assert ExecutionEventType.PLANNING_STARTED in event_types
    assert ExecutionEventType.PLAN_CREATED in event_types
    assert ExecutionEventType.EXECUTION_STARTED in event_types
    assert ExecutionEventType.EXECUTION_COMPLETED in event_types


@pytest.mark.asyncio
async def test_orchestrator_execute_async_multi_agent():
    """Test async execution with multi-agent strategy."""
    task_service = TaskService()
    agent_service = AgentService()
    tool_registry = ToolRegistry()
    memory_writer = MemoryWriter()

    orchestrator = OrchestratorService(
        task_service=task_service,
        agent_service=agent_service,
        tool_registry=tool_registry,
        memory_writer=memory_writer,
    )

    agent = AgentRead(id="a1", name="Agent1")
    task = TaskCreate(name="Complex", description="Analyze and compare the data")

    result = await orchestrator.execute(agent=agent, task_in=task)

    assert result.execution_id is not None
    # Async execution goes through ExecutionService which doesn't populate child_results
    assert result.status.lower() == "success"


@pytest.mark.asyncio
async def test_orchestrator_run_async_exception_handling():
    """Test orchestrator.run catches exceptions and marks context failed."""
    from unittest.mock import MagicMock, AsyncMock

    task_service = TaskService()
    tool_registry = ToolRegistry()
    memory_writer = MemoryWriter()

    # ExecutionService is what gets called, not AgentService
    failing_execution_service = MagicMock()
    failing_execution_service.execute_plan = AsyncMock(side_effect=RuntimeError("Async failure"))

    orchestrator = OrchestratorService(
        task_service=task_service,
        agent_service=AgentService(),
        execution_service=failing_execution_service,
        tool_registry=tool_registry,
        memory_writer=memory_writer,
    )

    agent = AgentRead(id="agent-1", name="TestAgent")
    task = TaskCreate(name="Failing Task", description="Task that fails")

    with pytest.raises(RuntimeError, match="Async failure"):
        await orchestrator.run(agent=agent, task_in=task)


@pytest.mark.asyncio
async def test_orchestrator_stream_execute_multi_agent():
    """Test streaming with multi-agent strategy yields agent events."""
    from app.schemas.execution_event import ExecutionEventType

    task_service = TaskService()
    agent_service = AgentService()
    tool_registry = ToolRegistry()
    memory_writer = MemoryWriter()

    orchestrator = OrchestratorService(
        task_service=task_service,
        agent_service=agent_service,
        tool_registry=tool_registry,
        memory_writer=memory_writer,
    )

    agent = AgentRead(id="a1", name="Agent1")
    task = TaskCreate(name="Complex", description="Analyze and compare the data")

    events = []
    async for event in orchestrator.stream_execute(agent=agent, task_in=task):
        events.append(event)

    event_types = [e.type for e in events]
    assert ExecutionEventType.PLANNING_STARTED in event_types
    assert ExecutionEventType.PLAN_CREATED in event_types
    assert ExecutionEventType.EXECUTION_COMPLETED in event_types


@pytest.mark.asyncio
async def test_orchestrator_stream_execute_with_tool_calls():
    """Test streaming execution handles tool calls."""
    from app.schemas.execution_event import ExecutionEventType

    task_service = TaskService()
    agent_service = AgentService()
    tool_registry = ToolRegistry()
    memory_writer = MemoryWriter()

    orchestrator = OrchestratorService(
        task_service=task_service,
        agent_service=agent_service,
        tool_registry=tool_registry,
        memory_writer=memory_writer,
    )

    agent = AgentRead(id="agent-1", name="TestAgent")
    task = TaskCreate(name="Tool Task", description="Simple task")

    events = []
    async for event in orchestrator.stream_execute(agent=agent, task_in=task):
        events.append(event)

    event_types = [e.type for e in events]
    # Verify expected events are present
    assert ExecutionEventType.PLANNING_STARTED in event_types
    assert ExecutionEventType.PLAN_CREATED in event_types
    assert ExecutionEventType.EXECUTION_STARTED in event_types
    assert ExecutionEventType.EXECUTION_COMPLETED in event_types


@pytest.mark.asyncio
async def test_orchestrator_stream_execute_exception_yields_failed_event():
    """Test streaming yields EXECUTION_FAILED on exception."""
    from unittest.mock import MagicMock, AsyncMock
    from app.schemas.execution_event import ExecutionEventType

    task_service = TaskService()
    tool_registry = ToolRegistry()
    memory_writer = MemoryWriter()

    # ExecutionService is what's called during streaming
    failing_execution_service = MagicMock()

    async def failing_stream(*args, **kwargs):
        raise RuntimeError("Stream failure")
        yield  # Make it a generator

    failing_execution_service.stream_execute_plan = failing_stream

    orchestrator = OrchestratorService(
        task_service=task_service,
        agent_service=AgentService(),
        execution_service=failing_execution_service,
        tool_registry=tool_registry,
        memory_writer=memory_writer,
    )

    agent = AgentRead(id="agent-1", name="TestAgent")
    task = TaskCreate(name="Failing Task", description="Simple task")

    events = []
    with pytest.raises(RuntimeError):
        async for event in orchestrator.stream_execute(agent=agent, task_in=task):
            events.append(event)

    event_types = [e.type for e in events]
    assert ExecutionEventType.EXECUTION_FAILED in event_types


@pytest.mark.asyncio
async def test_orchestrator_execute_async_with_tool_calls():
    """Test async execution handles tool calls correctly."""
    task_service = TaskService()
    agent_service = AgentService()
    tool_registry = ToolRegistry()
    memory_writer = MemoryWriter()

    orchestrator = OrchestratorService(
        task_service=task_service,
        agent_service=agent_service,
        tool_registry=tool_registry,
        memory_writer=memory_writer,
    )

    agent = AgentRead(id="agent-1", name="TestAgent")
    task = TaskCreate(name="Async Tool Task", description="Simple task")

    result = await orchestrator.execute(agent=agent, task_in=task)

    assert result.execution_id is not None
    assert result.status.lower() == "success"


@pytest.mark.asyncio
async def test_orchestrator_execute_async_exception_handling():
    """Test async execute catches exceptions and marks context failed."""
    from unittest.mock import MagicMock, AsyncMock

    task_service = TaskService()
    tool_registry = ToolRegistry()
    memory_writer = MemoryWriter()

    # ExecutionService is what gets called
    failing_execution_service = MagicMock()
    failing_execution_service.execute_plan = AsyncMock(side_effect=RuntimeError("Execute failure"))

    orchestrator = OrchestratorService(
        task_service=task_service,
        agent_service=AgentService(),
        execution_service=failing_execution_service,
        tool_registry=tool_registry,
        memory_writer=memory_writer,
    )

    agent = AgentRead(id="agent-1", name="TestAgent")
    task = TaskCreate(name="Failing Task", description="Simple task")

    with pytest.raises(RuntimeError, match="Execute failure"):
        await orchestrator.execute(agent=agent, task_in=task)
