from typing import List
from uuid import uuid4

from app.schemas.rag.chunk import Chunk
from app.schemas.rag.document import Document


class ChunkingService:
    """
    Splits documents into smaller chunks.
    """

    def chunk(self, document: Document, chunk_size: int = 500) -> List[Chunk]:
        chunks: List[Chunk] = []

        text = document.content
        for i in range(0, len(text), chunk_size):
            chunk_text = text[i:i + chunk_size]

            chunks.append(
                Chunk(
                    chunk_id=str(uuid4()),
                    document_id=document.id,
                    content=chunk_text,
                    metadata=document.metadata,
                )
            )

        return chunks
