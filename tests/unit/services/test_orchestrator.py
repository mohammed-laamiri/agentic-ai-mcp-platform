"""
Unit tests for OrchestratorService.
"""

from app.services.orchestrator import OrchestratorService
from app.services.agent_service import AgentService
from app.services.task_service import TaskService
from app.services.tool_registry import ToolRegistry
from app.services.memory_writer import MemoryWriter
from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate


def test_orchestrator_run_happy_path():
    """Test orchestrator executes a task and returns result."""
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

    result = orchestrator.run(agent=agent, task_in=task)

    assert result.name == "Orchestrated Task"
    assert result.description == "Orchestrated task"
    # Result is stored after execution
    assert result.result is not None


def test_orchestrator_execute_returns_execution_result():
    """Test orchestrator.execute returns ExecutionResult without persistence."""
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

    result = orchestrator.execute(agent=agent, task_in=task)

    # execute() returns ExecutionResult, not TaskRead
    assert result.execution_id is not None
    assert result.status == "SUCCESS"
