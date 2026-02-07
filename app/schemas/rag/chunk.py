# app/schemas/rag/chunk.py

from typing import Dict, Optional
from pydantic import BaseModel, Field


class Chunk(BaseModel):
    """
    Represents a chunk of text retrieved from a document,
    used for RAG (Retrieval-Augmented Generation) workflows.
    """

    chunk_id: str = Field(..., description="Unique identifier for the chunk")
    document_id: str = Field(..., description="Identifier of the source document")
    text: str = Field(..., description="The textual content of the chunk")
    metadata: Optional[Dict] = Field(
        default_factory=dict,
        description="Optional metadata associated with the chunk"
    )
