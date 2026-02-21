"""
RAG Service (ChromaDB-backed).

Responsible for:
- Document ingestion
- Vector storage
- Semantic retrieval

This service does NOT:
- Call LLMs
- Perform orchestration
- Execute agents

This is a pure retrieval service.
"""

from typing import List
import uuid

import chromadb
from chromadb.config import Settings


class RAGService:
    """
    Minimal Chroma-based retrieval service.
    """

    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        collection_name: str = "knowledge_base",
    ) -> None:
        self._client = chromadb.Client(
            Settings(
                persist_directory=persist_directory,
                anonymized_telemetry=False,
            )
        )

        self._collection = self._client.get_or_create_collection(
            name=collection_name
        )

    # =====================================================
    # Document ingestion
    # =====================================================

    def add_document(
        self,
        content: str,
        metadata: dict | None = None,
        document_id: str | None = None,
    ) -> str:
        """
        Add a document to the vector store.
        """

        doc_id = document_id or str(uuid.uuid4())

        self._collection.add(
            ids=[doc_id],
            documents=[content],
            metadatas=[metadata or {}],
        )

        return doc_id

    def add_documents(
        self,
        documents: List[str],
    ) -> List[str]:
        """
        Add multiple documents.
        """

        ids = [str(uuid.uuid4()) for _ in documents]

        self._collection.add(
            ids=ids,
            documents=documents,
        )

        return ids

    # =====================================================
    # Retrieval
    # =====================================================

    def retrieve(
        self,
        query: str,
        top_k: int = 3,
    ) -> List[str]:
        """
        Retrieve most relevant documents.
        """

        results = self._collection.query(
            query_texts=[query],
            n_results=top_k,
        )

        return results.get("documents", [[]])[0]

    # =====================================================
    # Maintenance
    # =====================================================

    def count(self) -> int:
        return self._collection.count()

    def clear(self) -> None:
        """
        Delete all documents.
        """
        self._client.delete_collection(self._collection.name)

        self._collection = self._client.get_or_create_collection(
            name=self._collection.name
        )