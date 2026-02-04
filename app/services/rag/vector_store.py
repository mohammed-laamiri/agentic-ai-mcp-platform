"""
Vector Store Service.

Responsible for persisting and retrieving vector embeddings.

Architectural role:
- Abstract vector persistence layer
- OpenSearch-first design (but storage-agnostic)
- Used by RetrievalService and IngestionService
- NO knowledge of agents or orchestration

Design principles:
- Deterministic interfaces
- Explicit metadata handling
- Future-proof for filters, namespaces, multi-index
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

from app.schemas.rag.embedding import Embedding
from app.schemas.rag.retrieval import RetrievalResult


class VectorStore(ABC):
    """
    Abstract Vector Store contract.

    Concrete implementations may include:
    - OpenSearchVectorStore
    - PineconeVectorStore
    - InMemoryVectorStore (for tests)

    This interface MUST remain stable.
    """

    # --------------------------------------------------
    # Index lifecycle
    # --------------------------------------------------

    @abstractmethod
    def create_index(
        self,
        index_name: str,
        dimension: int,
        metadata_schema: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Create a vector index.

        Args:
            index_name: Logical index name
            dimension: Embedding vector size
            metadata_schema: Optional schema for metadata fields
        """
        raise NotImplementedError

    # --------------------------------------------------
    # Write operations
    # --------------------------------------------------

    @abstractmethod
    def upsert_embeddings(
        self,
        index_name: str,
        embeddings: List[Embedding],
    ) -> None:
        """
        Insert or update embeddings.

        Args:
            index_name: Target index
            embeddings: List of Embedding objects
        """
        raise NotImplementedError

    # --------------------------------------------------
    # Read operations
    # --------------------------------------------------

    @abstractmethod
    def similarity_search(
        self,
        index_name: str,
        query_vector: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[RetrievalResult]:
        """
        Perform vector similarity search.

        Args:
            index_name: Target index
            query_vector: Query embedding
            top_k: Number of results to return
            filters: Optional metadata filters

        Returns:
            Ranked list of RetrievalResult
        """
        raise NotImplementedError


# ==================================================
# In-memory reference implementation (DEV / TEST)
# ==================================================

class InMemoryVectorStore(VectorStore):
    """
    Simple in-memory vector store.

    Used for:
    - Local development
    - Unit tests
    - Contract validation

    NOT for production.
    """

    def __init__(self) -> None:
        self._indices: Dict[str, Dict[str, Embedding]] = {}

    def create_index(
        self,
        index_name: str,
        dimension: int,
        metadata_schema: Optional[Dict[str, Any]] = None,
    ) -> None:
        if index_name not in self._indices:
            self._indices[index_name] = {}

    def upsert_embeddings(
        self,
        index_name: str,
        embeddings: List[Embedding],
    ) -> None:
        if index_name not in self._indices:
            raise ValueError(f"Index '{index_name}' does not exist")

        for emb in embeddings:
            self._indices[index_name][emb.id] = emb

    def similarity_search(
        self,
        index_name: str,
        query_vector: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[RetrievalResult]:
        if index_name not in self._indices:
            raise ValueError(f"Index '{index_name}' does not exist")

        results: List[RetrievalResult] = []

        for emb in self._indices[index_name].values():
            score = self._cosine_similarity(query_vector, emb.vector)

            results.append(
                RetrievalResult(
                    id=emb.id,
                    score=score,
                    content=emb.content,
                    metadata=emb.metadata,
                )
            )

        # Sort by similarity score
        results.sort(key=lambda r: r.score, reverse=True)

        return results[:top_k]

    # --------------------------------------------------
    # Utilities
    # --------------------------------------------------

    def _cosine_similarity(
        self,
        a: List[float],
        b: List[float],
    ) -> float:
        if len(a) != len(b):
            return 0.0

        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(y * y for y in b) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot / (norm_a * norm_b)
