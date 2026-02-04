"""
Embedding Service.

Responsible for converting text into vector representations
used by the RAG pipeline.

Design principles:
- Provider-agnostic interface
- Deterministic outputs
- No storage concerns
- Safe to mock / replace
"""

from abc import ABC, abstractmethod
from typing import List
import json

import boto3


# ==================================================
# Interface
# ==================================================

class EmbeddingService(ABC):
    """
    Abstract embedding service contract.
    """

    @abstractmethod
    def embed_text(self, text: str) -> List[float]:
        """
        Generate an embedding for a single text input.
        """
        raise NotImplementedError

    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple text inputs.
        """
        raise NotImplementedError


# ==================================================
# Amazon Bedrock Implementation
# ==================================================

class BedrockEmbeddingService(EmbeddingService):
    """
    Embedding service backed by Amazon Bedrock.

    Default model:
    - amazon.titan-embed-text-v1
    """

    def __init__(
        self,
        model_id: str = "amazon.titan-embed-text-v1",
        region_name: str = "us-east-1",
    ) -> None:
        self._model_id = model_id
        self._client = boto3.client(
            service_name="bedrock-runtime",
            region_name=region_name,
        )

    # ----------------------------------------------
    # Public API
    # ----------------------------------------------

    def embed_text(self, text: str) -> List[float]:
        embeddings = self._invoke_model([text])
        return embeddings[0]

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return self._invoke_model(texts)

    # ----------------------------------------------
    # Internal helpers
    # ----------------------------------------------

    def _invoke_model(self, texts: List[str]) -> List[List[float]]:
        """
        Invoke Bedrock embedding model.

        Handles both single and batch inputs.
        """
        payload = {
            "inputText": texts[0] if len(texts) == 1 else texts
        }

        response = self._client.invoke_model(
            modelId=self._model_id,
            body=json.dumps(payload),
            accept="application/json",
            contentType="application/json",
        )

        body = json.loads(response["body"].read())

        # Single embedding response
        if isinstance(body, dict) and "embedding" in body:
            return [body["embedding"]]

        # Batch embedding response
        if isinstance(body, dict) and "embeddings" in body:
            return body["embeddings"]

        raise RuntimeError(
            f"Unexpected Bedrock embedding response format: {body}"
        )
