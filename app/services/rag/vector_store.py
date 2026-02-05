"""
Vector Store Service.

Abstract vector persistence layer for RAG.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

from app.schemas.rag.embedding import Embedding
from app.schemas.rag.retrieval import RetrievalResult


class VectorStore(ABC):
    """
    Abstract Vector Store contract.
    """

    @abstractmethod
    def create_index(
        self,
        index_name: str,
        dimension: int,
        metadata_schema: Optional[Dict[str, Any]] = None,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def upsert_embeddings(
        self,
        index_name: str,
        embeddings: List[Embedding],
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def similarity_search(
        self,
        index_name: str,
        query_vector: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[RetrievalResult]:
        raise NotImplementedError


# ==================================================
# In-memory implementation (TEST / DEV)
# ==================================================

class InMemoryVectorStore(VectorStore):
    def __init__(self) -> None:
        self._indices: Dict[str, Dict[str, Embedding]] = {}

    def create_index(
        self,
        index_name: str,
        dimension: int,
        metadata_schema: Optional[Dict[str, Any]] = None,
    ) -> None:
        self._indices.setdefault(index_name, {})

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
                    chunk_id=emb.id,
                    content=emb.content,
                    score=score,
                )
            )

        results.sort(key=lambda r: r.score, reverse=True)
        return results[:top_k]

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(y * y for y in b) ** 0.5
        return dot / (norm_a * norm_b) if norm_a and norm_b else 0.0
