"""
Embedding schema.

Represents a vector embedding generated from a document chunk.
Used for similarity search inside vector stores.
"""

from typing import List, Dict, Optional
from pydantic import BaseModel, Field


class Embedding(BaseModel):
    """
    Vector representation of a document chunk.
    """

    chunk_id: str = Field(
        ...,
        description="Reference to the chunk that generated this embedding",
    )

    vector: List[float] = Field(
        ...,
        description="Numeric embedding vector produced by embedding model",
    )

    metadata: Dict[str, str] = Field(
        default_factory=dict,
        description="Optional metadata copied from chunk or added during ingestion",
    )

    model_name: Optional[str] = Field(
        default=None,
        description="Embedding model used (e.g. amazon.titan-embed-text-v1)",
    )
