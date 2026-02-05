from typing import List

from app.schemas.rag.retrieval import RetrievalResult
from app.schemas.rag.chunk import DocumentChunk
from app.services.rag.vector_store import InMemoryVectorStore


class RetrievalService:
    """
    Retrieves relevant chunks from vector store.
    """

    def __init__(
        self,
        vector_store: InMemoryVectorStore,
        chunks: List[DocumentChunk],
    ) -> None:
        self._vector_store = vector_store
        self._chunks = {c.chunk_id: c for c in chunks}

    def retrieve(
        self,
        query_vector: List[float],
        top_k: int = 5,
    ) -> List[RetrievalResult]:
        matches = self._vector_store.similarity_search(query_vector, top_k)

        results: List[RetrievalResult] = []
        for chunk_id, score in matches:
            chunk = self._chunks.get(chunk_id)
            if not chunk:
                continue

            results.append(
                RetrievalResult(
                    chunk_id=chunk_id,
                    content=chunk.content,
                    score=score,
                )
            )

        return results
