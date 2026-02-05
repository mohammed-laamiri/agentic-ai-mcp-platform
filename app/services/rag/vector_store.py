"""
Vector Store Service.

Responsible for persisting and retrieving vector embeddings.

Architectural role:
- Abstract vector persistence layer
- OpenSearch-first design (but storage-agnostic)
- Used by RetrievalService and IngestionService
- NO knowledge of agents or orchestration
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

from opensearchpy import OpenSearch

from app.schemas.rag.embedding import Embedding
from app.schemas.rag.retrieval import RetrievalResult


# ==================================================
# Interface
# ==================================================

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
# OpenSearch implementation (PROD)
# ==================================================

class OpenSearchVectorStore(VectorStore):
    """
    OpenSearch-backed vector store using KNN.
    """

    def __init__(
        self,
        host: str,
        port: int = 443,
        use_ssl: bool = True,
        http_auth: Optional[Any] = None,
    ) -> None:
        self._client = OpenSearch(
            hosts=[{"host": host, "port": port}],
            use_ssl=use_ssl,
            http_auth=http_auth,
        )

    def create_index(
        self,
        index_name: str,
        dimension: int,
        metadata_schema: Optional[Dict[str, Any]] = None,
    ) -> None:
        if self._client.indices.exists(index_name):
            return

        properties: Dict[str, Any] = {
            "vector": {
                "type": "knn_vector",
                "dimension": dimension,
            },
            "content": {"type": "text"},
        }

        if metadata_schema:
            for key, field_type in metadata_schema.items():
                properties[key] = {"type": field_type}

        body = {
            "settings": {
                "index": {
                    "knn": True,
                }
            },
            "mappings": {
                "properties": properties
            },
        }

        self._client.indices.create(index=index_name, body=body)

    def upsert_embeddings(
        self,
        index_name: str,
        embeddings: List[Embedding],
    ) -> None:
        for emb in embeddings:
            doc = {
                "vector": emb.vector,
                "content": emb.content,
            }
            if emb.metadata:
                doc.update(emb.metadata)

            self._client.index(
                index=index_name,
                id=emb.id,
                body=doc,
                refresh=True,
            )

    def similarity_search(
        self,
        index_name: str,
        query_vector: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[RetrievalResult]:
        query: Dict[str, Any] = {
            "size": top_k,
            "query": {
                "knn": {
                    "vector": {
                        "vector": query_vector,
                        "k": top_k,
                    }
                }
            },
        }

        response = self._client.search(
            index=index_name,
            body=query,
        )

        results: List[RetrievalResult] = []

        for hit in response["hits"]["hits"]:
            results.append(
                RetrievalResult(
                    chunk_id=hit["_id"],
                    content=hit["_source"].get("content", ""),
                    score=hit["_score"],
                )
            )

        return results


# ==================================================
# In-memory implementation (DEV / TEST)
# ==================================================

class InMemoryVectorStore(VectorStore):
    """
    Simple in-memory vector store.
    """

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

        scored: List[RetrievalResult] = []

        for emb in self._indices[index_name].values():
            score = self._cosine_similarity(query_vector, emb.vector)
            scored.append(
                RetrievalResult(
                    chunk_id=emb.id,
                    content=emb.content,
                    score=score,
                )
            )

        scored.sort(key=lambda r: r.score, reverse=True)
        return scored[:top_k]

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        if len(a) != len(b):
            return 0.0

        dot = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(y * y for y in b) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot / (norm_a * norm_b)
