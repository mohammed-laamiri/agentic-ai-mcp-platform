import pytest

from app.services.orchestrator import OrchestratorService
from app.services.agent_service import AgentService
from app.services.task_service import TaskService
from app.services.memory_writer import MemoryWriter
from app.services.tool_registry import ToolRegistry
from app.repositories.execution_history_repository import ExecutionHistoryRepository
from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate

# ==================================================
# Fixtures
# ==================================================

@pytest.fixture
def agent_service():
    return AgentService()


@pytest.fixture
def task_service():
    return TaskService()


@pytest.fixture
def memory_writer():
    return MemoryWriter()


@pytest.fixture
def tool_registry():
    return ToolRegistry()


@pytest.fixture
def history_repo():
    return ExecutionHistoryRepository()


@pytest.fixture
def orchestrator(agent_service, task_service, tool_registry, memory_writer, history_repo):
    return OrchestratorService(
        task_service=task_service,
        agent_service=agent_service,
        tool_registry=tool_registry,
        memory_writer=memory_writer,
        execution_history_repo=history_repo,
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

def test_execution_history_saved(orchestrator, test_agent, simple_task, history_repo):
    orchestrator.execute(test_agent, simple_task)

    all_history = history_repo.all()
    assert len(all_history) == 1
    record = all_history[0]

    assert record["metadata"]["task_id"] is not None
    assert record["metadata"]["run_id"] is not None
    assert record["metadata"]["status"] in ["pending", "SUCCESS", "completed"]
    assert record["result"].status is not None
