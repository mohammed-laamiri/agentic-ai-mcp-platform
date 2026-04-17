"""
Unit tests for RAGService.

Tests document ingestion and retrieval using ChromaDB.
"""

import pytest

from app.services.rag.rag_service import RAGService


@pytest.mark.asyncio
async def test_rag_service_add_and_retrieve_documents(tmp_path):
    """
    RAGService should add documents and retrieve them by query.
    """
    # Setup isolated RAG DB
    rag = RAGService(
        persist_directory=str(tmp_path),
        collection_name="test_collection",
    )

    # Add documents (async)
    doc_ids = await rag.add_documents(
        documents=["Python is a programming language.", "FastAPI is a web framework."],
        metadatas=[{"source": "doc1"}, {"source": "doc2"}],
    )

    assert len(doc_ids) == 2

    # Retrieve by query (async)
    results = await rag.retrieve(query="What is Python?", top_k=1)

    assert len(results) >= 1
    assert "Python" in results[0]


@pytest.mark.asyncio
async def test_rag_service_retrieve_empty_collection(tmp_path):
    """
    RAGService should return empty list when collection is empty.
    """
    rag = RAGService(
        persist_directory=str(tmp_path),
        collection_name="empty_collection",
    )

    results = await rag.retrieve(query="test query", top_k=3)

    assert results == []
