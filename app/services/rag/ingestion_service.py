"""
RAG Ingestion Service

Responsible for:
- Preparing documents for vector storage
- Chunking long texts
- Attaching metadata
- Delegating storage to RAGService

Does NOT:
- Perform retrieval
- Execute agents
- Call LLMs
"""

from typing import List, Optional
from app.services.rag.rag_service import RAGService


class RAGIngestionService:
    """
    Handles document preprocessing before storage in ChromaDB.
    """

    def __init__(
        self,
        rag_service: RAGService,
        chunk_size: int = 500,
    ) -> None:
        self._rag_service = rag_service
        self._chunk_size = chunk_size

    # =====================================================
    # Public API
    # =====================================================

    def ingest_text(
        self,
        text: str,
        metadata: Optional[dict] = None,
    ) -> List[str]:
        """
        Ingest raw text by splitting into chunks.
        Returns list of document IDs.
        """

        chunks = self._chunk_text(text)
        metadatas = [metadata or {} for _ in chunks]

        return self._rag_service.add_documents(
            documents=chunks,
            metadatas=metadatas,
        )

    def ingest_batch(
        self,
        documents: List[str],
        metadata: Optional[List[dict]] = None,
    ) -> List[str]:
        """
        Ingest multiple independent documents.
        """
        return self._rag_service.add_documents(
            documents=documents,
            metadatas=metadata,
        )

    # =====================================================
    # Internal
    # =====================================================

    def _chunk_text(self, text: str) -> List[str]:
        """
        Simple character-based chunking.

        Later:
        - Replace with token-based chunking
        - Add overlap support
        """
        chunks = []

        for i in range(0, len(text), self._chunk_size):
            chunk = text[i : i + self._chunk_size]
            chunks.append(chunk)

        return chunks