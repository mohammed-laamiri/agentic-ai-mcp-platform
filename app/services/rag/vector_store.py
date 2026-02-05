from typing import Dict, List, Tuple
import math

from app.schemas.rag.embedding import EmbeddingVector


class InMemoryVectorStore:
    """
    Simple in-memory vector store.
    """

    def __init__(self) -> None:
        self._store: Dict[str, EmbeddingVector] = {}

    def upsert(self, embedding: EmbeddingVector) -> None:
        self._store[embedding.id] = embedding

    def similarity_search(
        self,
        query_vector: List[float],
        top_k: int = 5,
    ) -> List[Tuple[str, float]]:
        results = []

        for emb in self._store.values():
            score = self._cosine_similarity(query_vector, emb.vector)
            results.append((emb.id, score))

        results.sort(key=lambda x: x[1], reverse=True)
        return results[:top_k]

    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        dot = sum(a * b for a, b in zip(v1, v2))
        mag1 = math.sqrt(sum(a * a for a in v1))
        mag2 = math.sqrt(sum(b * b for b in v2))

        if mag1 == 0 or mag2 == 0:
            return 0.0

        return dot / (mag1 * mag2)
