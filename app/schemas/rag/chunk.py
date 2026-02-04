"""
Chunk schema.

Represents a semantically meaningful piece of a document
produced during the chunking phase of RAG ingestion.

Chunks are:
- Stored in the vector store
- Retrieved during query-time
- Passed to agents as context
"""

from typing import Dict, Optional
from pydantic import BaseModel, Field


class Chunk(BaseModel):
    """
    A single retrievable chunk of text.
    """

    chunk_id: str = Field(
        ...,
        description="Unique identifier for the chunk",
    )

    document_id: str = Field(
        ...,
        description="Identifier of the source document",
    )

    text: str = Field(
        ...,
        description="Chunk textual content",
    )

    metadata: Dict[str, str] = Field(
        default_factory=dict,
        description="Additional metadata (page, section, tags, etc.)",
    )

    score: Optional[float] = Field(
        default=None,
        description="Similarity score (set at retrieval time)",
    )
