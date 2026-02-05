from pydantic import BaseModel
from typing import List


class EmbeddingVector(BaseModel):
    """
    Vector representation of text.
    """
    id: str
    vector: List[float]
