from pydantic import BaseModel
from typing import List


class RetrievalResult(BaseModel):
    """
    Retrieved chunk + similarity score.
    """
    chunk_id: str
    content: str
    score: float
