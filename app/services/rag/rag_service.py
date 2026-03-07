"""
RAG Service (ChromaDB-backed, Async-Ready).

Responsible for:
- Document ingestion
- Vector storage
- Semantic retrieval
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
    # Synchronous helper (for tests / legacy code)
    # ----------------------------------------------------
    def add_document(
        self,
        content: Optional[str] = None,
        metadata: Optional[dict] = None,
        document_id: Optional[str] = None,
    ) -> None:
        """
        Adds a single document to the collection synchronously.
        Ensures metadata is always a non-empty dict.
        Accepts both 'content' and 'document_id' keywords for test compatibility.
        """
        doc_content = content or ""
        doc_id = document_id or str(uuid.uuid4())
        doc_metadata = metadata if metadata is not None else {}

        # ChromaDB requires metadata to be a dict (cannot be None)
        if not doc_metadata:
            doc_metadata = {"_placeholder": True}

        embeddings = None
        if self._embedding_service:
            embeddings = self._embedding_service.embed([doc_content])

        self._collection.add(
            ids=[doc_id],
            documents=[doc_content],
            metadatas=[doc_metadata],
            embeddings=embeddings,
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

        # Ensure all metadatas are non-empty dicts
        safe_metadatas = []
        for md in (metadatas or [{} for _ in documents]):
            safe_metadatas.append(md if md else {"_placeholder": True})

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
            metadatas=safe_metadatas,
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
        return documents[0] if documents else []