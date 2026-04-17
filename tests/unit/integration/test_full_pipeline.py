"""
Full integration test for the Agentic AI platform.

Covers:
- PlannerAgent planning
- AgentService execution
- OrchestratorService end-to-end (async and streaming)
"""

import pytest

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
from app.schemas.execution_event import ExecutionEventType
from app.services.agent_service import AgentService
from app.services.orchestrator import OrchestratorService
from app.services.task_service import TaskService
from app.services.planner_agent import PlannerAgent
from app.services.tool_registry import ToolRegistry
from app.services.memory_writer import MemoryWriter


@pytest.mark.asyncio
async def test_full_pipeline_single_agent():
    """
    Full pipeline test for a simple single-agent task.
    """
    # Initialize services
    task_service = TaskService()
    agent_service = AgentService()
    planner_agent = PlannerAgent()
    tool_registry = ToolRegistry()
    memory_writer = MemoryWriter()

    orchestrator = OrchestratorService(
        task_service=task_service,
        agent_service=agent_service,
        planner_agent=planner_agent,
        tool_registry=tool_registry,
        memory_writer=memory_writer,
    )

    # Define agent and task
    agent = AgentRead(id="agent-1", name="TestAgent")
    task = TaskCreate(name="Simple Task", description="Simple task")

    # Run orchestrator (async)
    task_read = await orchestrator.run(agent=agent, task_in=task)

    # Assertions
    assert task_read is not None
    assert task_read.result is not None


@pytest.mark.asyncio
async def test_full_pipeline_multi_agent():
    """
    Full pipeline test for a complex multi-agent task.
    """
    # Initialize services
    task_service = TaskService()
    agent_service = AgentService()
    planner_agent = PlannerAgent()
    tool_registry = ToolRegistry()
    memory_writer = MemoryWriter()

    orchestrator = OrchestratorService(
        task_service=task_service,
        agent_service=agent_service,
        planner_agent=planner_agent,
        tool_registry=tool_registry,
        memory_writer=memory_writer,
    )

    # Define agent and task (complex triggers MULTI_AGENT)
    agent = AgentRead(id="agent-1", name="TestAgent")
    task = TaskCreate(name="Complex Task", description="Analyze and summarize data")

    # Run orchestrator (async)
    task_read = await orchestrator.run(agent=agent, task_in=task)

    # Assertions
    assert task_read is not None
    assert task_read.result is not None


@pytest.mark.asyncio
async def test_stream_execute_events():
    """
    Test streaming execution events from OrchestratorService.
    """
    # Initialize services
    task_service = TaskService()
    agent_service = AgentService()
    planner_agent = PlannerAgent()
    tool_registry = ToolRegistry()
    memory_writer = MemoryWriter()

    orchestrator = OrchestratorService(
        task_service=task_service,
        agent_service=agent_service,
        planner_agent=planner_agent,
        tool_registry=tool_registry,
        memory_writer=memory_writer,
    )

    agent = AgentRead(id="agent-1", name="TestAgent")
    task = TaskCreate(name="Stream Task", description="Stream test task")

    events = []
    async for event in orchestrator.stream_execute(agent=agent, task_in=task):
        events.append(event)

    # Validate event types
    event_types = [e.type for e in events]
    assert ExecutionEventType.PLANNING_STARTED in event_types
    assert ExecutionEventType.PLAN_CREATED in event_types
    assert ExecutionEventType.EXECUTION_STARTED in event_types
    assert ExecutionEventType.EXECUTION_COMPLETED in event_types
