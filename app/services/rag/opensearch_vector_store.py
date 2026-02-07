"""
OpenSearch Vector Store implementation.
"""

from typing import List, Dict, Any, Optional

from opensearchpy import OpenSearch

from app.schemas.rag.embedding import Embedding
from app.schemas.rag.retrieval import RetrievalResult
from app.services.rag.vector_store import VectorStore


class OpenSearchVectorStore(VectorStore):
    def __init__(self, client: OpenSearch) -> None:
        self._client = client

    def create_index(
        self,
        index_name: str,
        dimension: int,
        metadata_schema: Optional[Dict[str, Any]] = None,
    ) -> None:
        if self._client.indices.exists(index=index_name):
            return

        body = {
            "mappings": {
                "properties": {
                    "vector": {
                        "type": "knn_vector",
                        "dimension": dimension,
                    },
                    "content": {"type": "text"},
                }
            }
        }

        self._client.indices.create(index=index_name, body=body)

    def upsert_embeddings(
        self,
        index_name: str,
        embeddings: List[Embedding],
    ) -> None:
        for emb in embeddings:
            self._client.index(
                index=index_name,
                id=emb.id,
                body={
                    "vector": emb.vector,
                    "content": emb.content,
                    "metadata": emb.metadata,
                },
            )

    def similarity_search(
        self,
        index_name: str,
        query_vector: List[float],
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[RetrievalResult]:
        query = {
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

        response = self._client.search(index=index_name, body=query)

        results: List[RetrievalResult] = []
        for hit in response["hits"]["hits"]:
            src = hit["_source"]
            results.append(
                RetrievalResult(
                    chunk_id=hit["_id"],
                    content=src["content"],
                    score=hit["_score"],
                )
            )

        return results
