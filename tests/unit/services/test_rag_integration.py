"""
Unit tests for AgentService + RAG integration.

Validates that AgentService can retrieve context from RAG
and return a successful ExecutionResult.
"""

import pytest
from app.services.agent_service import AgentService
from app.services.rag.rag_service import RAGService
from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate


@pytest.mark.asyncio
async def test_agent_service_execute_with_rag():
    # ----------------------------
    # Initialize RAG service
    # ----------------------------
    rag = RAGService()
    # NOTE: add_document is sync in your current RAGService
    rag.add_document(content="Relevant RAG context 1")
    rag.add_document(content="Relevant RAG context 2")

    # ----------------------------
    # Initialize AgentService with RAG
    # ----------------------------
    service = AgentService(rag_service=rag)

    agent = AgentRead(id="agent-1", name="TestAgent")
    task = TaskCreate(description="Test task that needs RAG context")

    # ----------------------------
    # Execute agent
    # ----------------------------
    result = await service.execute(agent=agent, task=task)

    # ----------------------------
    # Validate execution
    # ----------------------------
    assert result.status == "success"
    assert result.error is None
    assert "Relevant RAG context 1" in result.output or "Relevant RAG context 2" in result.output
    assert "agent-1" in result.output
    assert "Test task" in result.output