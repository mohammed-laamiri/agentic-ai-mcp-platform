"""
Embedding Service Abstraction

Provides a pluggable embedding layer.

Responsibilities:
- Convert text into vector embeddings
- Abstract embedding provider
- Allow swapping providers without touching RAGService
"""

from typing import List
from abc import ABC, abstractmethod


class BaseEmbeddingService(ABC):
    """
    Abstract embedding interface.
    """

    @abstractmethod
    def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Convert list of texts into list of vectors.
        """
        pass


# -------------------------------------------------------
# Default Placeholder Implementation
# -------------------------------------------------------

class DummyEmbeddingService(BaseEmbeddingService):
    """
    Development / testing embedding implementation.

    Returns zero vectors.
    Replace with real provider later.
    """

    def __init__(self, dimension: int = 384) -> None:
        self._dimension = dimension

    def embed(self, texts: List[str]) -> List[List[float]]:
        return [[0.0] * self._dimension for _ in texts]