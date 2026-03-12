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
    assert result.status == "SUCCESS"


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
    """_validate_plan raises when SINGLE_AGENT has steps."""
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
    plan = ExecutionPlan(
        strategy=ExecutionStrategy.SINGLE_AGENT,
        steps=[agent],
        reason="test",
    )
    task = TaskCreate(name="T", description="d")
    context = AgentExecutionContext()

    with pytest.raises(ValueError, match="SINGLE_AGENT must not define steps"):
        orchestrator._execute_plan_sync(agent, task, plan, context)


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
    from app.schemas.agent_execution_context import AgentExecutionContext
    agent = AgentRead(id="a1", name="A1")
    plan = ExecutionPlan(
        strategy=ExecutionStrategy.MULTI_AGENT,
        steps=[agent],
        reason="test",
    )
    task = TaskCreate(name="T", description="d")
    context = AgentExecutionContext()

    with pytest.raises(ValueError, match="MULTI_AGENT requires at least two"):
        orchestrator._execute_plan_sync(agent, task, plan, context)


def test_orchestrator_execute_sync_with_tool_calls_in_context():
    """When agent returns tool_calls, orchestrator runs execute_batch and merges tool results."""
    from unittest.mock import MagicMock

    task_service = TaskService()
    tool_registry = ToolRegistry()
    memory_writer = MemoryWriter()
    # Agent that declares a tool call
    agent_stub = MagicMock()
    agent_stub.execute = MagicMock(
        return_value={
            "execution_id": "e1",
            "agent_id": "a1",
            "agent_name": "A1",
            "input": "in",
            "output": "out",
            "status": "SUCCESS",
            "tool_calls": [{"tool_id": "no-such-tool", "arguments": {}}],
        }
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
    # Tool phase ran (batch executed; may have child_results from failed tool)
    assert result.child_results is not None


def test_orchestrator_execute_sync_exception_marks_context_failed():
    """When execution raises, context is marked failed and exception is re-raised."""
    from unittest.mock import MagicMock

    task_service = TaskService()
    tool_registry = ToolRegistry()
    memory_writer = MemoryWriter()
    failing_agent = MagicMock()
    failing_agent.execute = MagicMock(side_effect=RuntimeError("Agent failed"))
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
    assert result.status == "SUCCESS"


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
    assert result.child_results is not None
    assert len(result.child_results) >= 2
