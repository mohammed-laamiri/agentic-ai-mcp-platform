from typing import List
import random

from app.schemas.rag.embedding import EmbeddingVector
from app.schemas.rag.chunk import DocumentChunk


class EmbeddingService:
    """
    Generates embeddings (mocked for now).
    """

    def embed(self, chunk: DocumentChunk) -> EmbeddingVector:
        # TEMP: deterministic fake embedding
        vector = [random.random() for _ in range(128)]

        return EmbeddingVector(
            id=chunk.chunk_id,
            vector=vector,
        )
