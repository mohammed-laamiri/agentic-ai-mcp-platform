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

from typing import List, Optional
import uuid
import chromadb
from chromadb.config import Settings
from app.services.rag.embedding_service import BaseEmbeddingService


class RAGService:

    def __init__(
        self,
        persist_directory: str = "./chroma_db",
        collection_name: str = "knowledge_base",
        embedding_service: Optional[BaseEmbeddingService] = None,
    ) -> None:

        self._embedding_service = embedding_service

        self._client = chromadb.Client(
            Settings(
                persist_directory=persist_directory,
                anonymized_telemetry=False,
                is_persistent=True,
            )
        )

        self._collection_name = collection_name

        self._collection = self._client.get_or_create_collection(
            name=self._collection_name
        )

    # ----------------------------------------------------
    # Ingestion
    # ----------------------------------------------------

    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[dict]] = None,
    ) -> List[str]:

        ids = [str(uuid.uuid4()) for _ in documents]

        embeddings = None
        if self._embedding_service:
            embeddings = self._embedding_service.embed(documents)

        self._collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas if metadatas else [{} for _ in documents],
            embeddings=embeddings,
        )

        return ids

    # ----------------------------------------------------
    # Retrieval
    # ----------------------------------------------------

    def retrieve(self, query: str, top_k: int = 3) -> List[str]:

        if self._embedding_service:
            query_embedding = self._embedding_service.embed([query])[0]

            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
            )
        else:
            results = self._collection.query(
                query_texts=[query],
                n_results=top_k,
            )

        documents = results.get("documents", [])
        if not documents:
            return []

        return documents[0]