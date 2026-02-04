"""
Retrieval Service.

Responsible for:
- Querying the VectorStore
- Returning relevant chunks for a user query
- Acting as the read-path of the RAG pipeline

Architectural role:
- Stateless
- Pure retrieval (no LLM calls)
- Orchestrator-agnostic
- Embedding-agnostic (expects pre-embedded query)

Future enhancements:
- Hybrid search (keyword + vector)
- Metadata filtering
- Re-ranking
- Multi-index routing
"""

from typing import List

from app.services.rag.vector_store import VectorStore
from app.schemas.rag.retrieval import RetrievalResult
from app.schemas.rag.chunk import Chunk
from app.schemas.rag.embedding import Embedding


class RetrievalService:
    """
    Executes vector similarity search against the VectorStore.
    """

    def __init__(
        self,
        vector_store: VectorStore,
        top_k: int = 5,
    ) -> None:
        self._vector_store = vector_store
        self._top_k = top_k

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def retrieve(
        self,
        query_embedding: Embedding,
    ) -> RetrievalResult:
        """
        Retrieve relevant chunks for a query embedding.

        Args:
            query_embedding: Embedded representation of the user query

        Returns:
            RetrievalResult containing ranked chunks
        """
        matches = self._vector_store.search(
            embedding=query_embedding.vector,
            top_k=self._top_k,
        )

        chunks: List[Chunk] = [match.chunk for match in matches]

        return RetrievalResult(
            chunks=chunks,
            total=len(chunks),
        )
