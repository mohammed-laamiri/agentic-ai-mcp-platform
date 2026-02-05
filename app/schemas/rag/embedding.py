"""
Embedding schema.

Represents a vector embedding produced from text.

Used for:
- Documents
- Chunks
- Queries
"""

from typing import List
from pydantic import BaseModel, Field


class Embedding(BaseModel):
    """
    Vector embedding representation.
    """

    vector: List[float] = Field(
        ...,
        description="Numerical embedding vector",
    )

    model: str = Field(
        ...,
        description="Embedding model identifier",
    )

    dimension: int = Field(
        ...,
        description="Vector dimensionality",
    )
