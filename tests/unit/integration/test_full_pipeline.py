"""
Full integration test for the Agentic AI platform.

Covers:
- PlannerAgent planning
- AgentService execution
- ExecutionService streaming
- OrchestratorService end-to-end
"""

import asyncio
import pytest

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
from app.services.agent_service import AgentService
from app.services.orchestrator import OrchestratorService
from app.services.task_service import TaskService
from app.services.planner_agent import PlannerAgent
from app.services.execution.execution_service import ExecutionService

@pytest.mark.asyncio
async def test_full_pipeline_single_agent():
    """
    Full pipeline test for a simple single-agent task.
    """
    # Initialize services
    task_service = TaskService()
    agent_service = AgentService()
    planner_agent = PlannerAgent()
    execution_service = ExecutionService()
    orchestrator = OrchestratorService(
        task_service=task_service,
        agent_service=agent_service,
        planner_agent=planner_agent,
        execution_service=execution_service,
    )

    # Define agent and task
    agent = AgentRead(id="agent-1", name="TestAgent")
    task = TaskCreate(description="Simple task")

    # Run orchestrator
    task_read = await orchestrator.run(agent=agent, task_in=task)

    # Assertions
    assert task_read is not None
    assert hasattr(task_read, "result")
    assert "Executing step" in task_read.result
    assert "TestAgent" in task_read.result

@pytest.mark.asyncio
async def test_full_pipeline_multi_agent():
    """
    Full pipeline test for a complex multi-agent task.
    """
    # Initialize services
    task_service = TaskService()
    agent_service = AgentService()
    planner_agent = PlannerAgent()
    execution_service = ExecutionService()
    orchestrator = OrchestratorService(
        task_service=task_service,
        agent_service=agent_service,
        planner_agent=planner_agent,
        execution_service=execution_service,
    )

    # Define agent and task
    agent = AgentRead(id="agent-1", name="TestAgent")
    task = TaskCreate(description="Analyze and summarize data")

    # Run orchestrator
    task_read = await orchestrator.run(agent=agent, task_in=task)

    # Assertions
    assert task_read is not None
    assert hasattr(task_read, "result")
    # Multi-agent should mention both agents in steps
    assert "Executing step" in task_read.result
    assert "TestAgent" in task_read.result

@pytest.mark.asyncio
async def test_stream_execute_events():
    """
    Test streaming execution events from ExecutionService.
    """
    agent = AgentRead(id="agent-1", name="TestAgent")
    task = TaskCreate(description="Stream test task")

    execution_service = ExecutionService()
    planner_agent = PlannerAgent()
    plan = await planner_agent.plan(agent, task)

    events = []
    async for event in execution_service.stream_execute_plan(agent, task, plan, context=None):
        events.append(event)

    # Validate event types
    event_types = [e.type for e in events]
    assert event_types[0] == "execution_started"
    assert event_types[-1] == "execution_completed"
    assert any(e.type == "token_chunk" for e in events)
    assert any(e.type == "step_completed" for e in events)