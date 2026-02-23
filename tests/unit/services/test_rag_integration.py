"""
Unit tests for AgentService with RAG integration.
"""

from app.services.agent_service import AgentService
from app.services.rag.rag_service import RAGService
from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate


def test_agent_service_execute_with_rag(tmp_path):
    """
    AgentService should include retrieved RAG context in output.
    """

    # ----------------------------------------
    # Setup isolated RAG DB
    # ----------------------------------------

    rag = RAGService(
        persist_directory=str(tmp_path),
        collection_name="test_collection",
    )

    rag.add_document(
        content="Python is a programming language.",
        document_id="doc1",
    )

    # ----------------------------------------
    # Create AgentService with RAG
    # ----------------------------------------

    service = AgentService(rag_service=rag)

    agent = AgentRead(
        id="agent1",
        name="TestAgent",
        description="Test agent",
    )

    task = TaskCreate(
        name="Test Task",
        description="What is Python?",
    )

    # ----------------------------------------
    # Execute
    # ----------------------------------------

    result = service.execute(agent=agent, task=task)

    # ----------------------------------------
    # Assertions
    # ----------------------------------------

    assert isinstance(result, dict)

    assert result["agent_name"] == "TestAgent"

    assert "Python is a programming language." in result["output"]

    assert "Retrieved Context" in result["output"]