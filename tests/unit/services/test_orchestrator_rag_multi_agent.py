# tests/unit/services/test_orchestrator_rag_multi_agent.py

from unittest.mock import Mock
import pytest

from app.schemas.execution_strategy import ExecutionStrategy
from app.schemas.execution_plan import ExecutionPlan
from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
from app.schemas.rag.chunk import Chunk
from app.services.orchestrator import Orchestrator


# ---------------------------------------------------------
# Fixtures
# ---------------------------------------------------------

@pytest.fixture
def orchestrator() -> Orchestrator:
    """
    Provides a fully mocked Orchestrator for testing the
    multi-agent RAG execution flow while respecting the
    real constructor dependencies.
    """

    task_service = Mock()
    agent_service = Mock()
    tool_registry = Mock()
    memory_writer = Mock()

    orch = Orchestrator(
        task_service=task_service,
        agent_service=agent_service,
        tool_registry=tool_registry,
        memory_writer=memory_writer,
    )

    # Attach optional services used in RAG paths
    orch._planner_agent = Mock()
    orch._agent_service = agent_service
    orch._retrieval_service = Mock()

    return orch


# ---------------------------------------------------------
# Tests
# ---------------------------------------------------------

def test_multi_agent_rag_flow(orchestrator: Orchestrator):
    # -------------------------------
    # Create mock agents
    # -------------------------------
    agent_1 = AgentRead(id="agent-1", name="Agent One")
    agent_2 = AgentRead(id="agent-2", name="Agent Two")

    # -------------------------------
    # Create task with embedding
    # -------------------------------
    task = TaskCreate(
        description="Test RAG multi-agent task",
        input={"query": "user question"},
        embedding=[0.1, 0.2, 0.3],
    )

    # -------------------------------
    # Mock retrieval service to return valid chunks
    # -------------------------------
    orchestrator._retrieval_service.retrieve = Mock(
        return_value=[
            Chunk(
                chunk_id="chunk-1",
                document_id="doc-1",
                text="knowledge 1",
                metadata={},
            ),
            Chunk(
                chunk_id="chunk-2",
                document_id="doc-2",
                text="knowledge 2",
                metadata={},
            ),
        ]
    )

    # -------------------------------
    # Mock planner_agent.plan for multi-agent strategy
    # -------------------------------
    orchestrator._planner_agent.plan = Mock(
        return_value=ExecutionPlan(
            strategy=ExecutionStrategy.MULTI_AGENT,
            steps=[agent_1, agent_2],
        )
    )

    # -------------------------------
    # Mock agent_service.execute results
    # -------------------------------
    orchestrator._agent_service.execute = Mock(
        side_effect=[
            {"output": "agent-1 result", "tool_calls": []},
            {"output": "agent-2 result", "tool_calls": []},
        ]
    )

    # -------------------------------
    # Execute orchestrator
    # -------------------------------
    result = orchestrator.execute(agent_1, task)

    # -------------------------------
    # Assertions
    # -------------------------------
    assert result.output == "agent-2 result"
    assert orchestrator._agent_service.execute.call_count == 2

    orchestrator._retrieval_service.retrieve.assert_called_once_with(
        query_embedding=[0.1, 0.2, 0.3]
    )
