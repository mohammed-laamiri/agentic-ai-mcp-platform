from typing import List

from app.schemas.rag.document import Document
from app.schemas.rag.chunk import Chunk
from app.services.rag.chunking_service import ChunkingService
from app.services.rag.embedding_service import EmbeddingService
from app.services.rag.vector_store import InMemoryVectorStore


class RAGIngestionService:
    """
    End-to-end ingestion pipeline.
    """

    def __init__(
        self,
        chunker: ChunkingService,
        embedder: EmbeddingService,
        vector_store: InMemoryVectorStore,
    ) -> None:
        self._chunker = chunker
        self._embedder = embedder
        self._vector_store = vector_store
        self._chunks: List[Chunk] = []

    def ingest(self, document: Document) -> List[Chunk]:
        chunks = self._chunker.chunk(document)

        for chunk in chunks:
            embedding = self._embedder.embed(chunk)
            self._vector_store.upsert(embedding)

        self._chunks.extend(chunks)
        return chunks

    @property
    def chunks(self) -> List[Chunk]:
        return self._chunks
