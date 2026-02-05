"""
Retrieval Service.

Responsible for:
- Querying the VectorStore
- Returning relevant results for a query embedding
- Acting as the read-path of the RAG pipeline

Architectural role:
- Stateless
- Pure retrieval (no LLM calls)
- Orchestrator-agnostic
- Embedding-agnostic (expects pre-embedded query)
"""

from typing import List

from app.services.rag.vector_store import VectorStore
from app.schemas.rag.retrieval import RetrievalResult
from app.schemas.rag.embedding import Embedding


class RetrievalService:
    """
    Executes vector similarity search against the VectorStore.
    """

    def __init__(
        self,
        vector_store: VectorStore,
        index_name: str,
        top_k: int = 5,
    ) -> None:
        self._vector_store = vector_store
        self._index_name = index_name
        self._top_k = top_k

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def retrieve(
        self,
        query_embedding: Embedding,
    ) -> List[RetrievalResult]:
        """
        Retrieve relevant results for a query embedding.

        Args:
            query_embedding: Embedded representation of the user query

        Returns:
            Ranked list of RetrievalResult
        """
        return self._vector_store.similarity_search(
            index_name=self._index_name,
            query_vector=query_embedding.vector,
            top_k=self._top_k,
        )
