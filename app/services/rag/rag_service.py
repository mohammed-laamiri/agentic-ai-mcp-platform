"""
RAG Service (ChromaDB-backed, Async-Ready).

Responsible for:
- Document ingestion
- Vector storage
- Semantic retrieval

Phase 3 Upgrade:
- Public methods are async
- Blocking operations executed safely in threadpool
- Backwards architecture preserved

This service does NOT:
- Call LLMs
- Perform orchestration
- Execute agents
"""

from typing import List, Optional
import uuid
import asyncio
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
    # Ingestion (Async-safe)
    # ----------------------------------------------------

    async def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[dict]] = None,
    ) -> List[str]:

        ids = [str(uuid.uuid4()) for _ in documents]

        embeddings = None

        if self._embedding_service:
            embeddings = await asyncio.to_thread(
                self._embedding_service.embed,
                documents,
            )

        await asyncio.to_thread(
            self._collection.add,
            ids=ids,
            documents=documents,
            metadatas=metadatas if metadatas else [{} for _ in documents],
            embeddings=embeddings,
        )

        return ids

    # ----------------------------------------------------
    # Retrieval (Async-safe)
    # ----------------------------------------------------

    async def retrieve(self, query: str, top_k: int = 3) -> List[str]:

        if self._embedding_service:
            query_embedding = await asyncio.to_thread(
                self._embedding_service.embed,
                [query],
            )

            results = await asyncio.to_thread(
                self._collection.query,
                query_embeddings=[query_embedding[0]],
                n_results=top_k,
            )
        else:
            results = await asyncio.to_thread(
                self._collection.query,
                query_texts=[query],
                n_results=top_k,
            )

        documents = results.get("documents", [])

        if not documents:
            return []

        return documents[0]