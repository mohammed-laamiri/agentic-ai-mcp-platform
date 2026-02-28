"""
Bedrock Embedding Service (Production Hardened)

Features:
- Exponential backoff retries
- Configurable timeout
- Controlled max attempts
- Clean error handling
- AWS SDK config tuning

Requires:
- boto3
- botocore
"""

from typing import List
import json
import time

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, BotoCoreError

from app.services.rag.embedding_service import BaseEmbeddingService


class BedrockEmbeddingService(BaseEmbeddingService):
    """
    Production-grade Amazon Bedrock embedding service.
    """

    def __init__(
        self,
        model_id: str = "amazon.titan-embed-text-v1",
        region_name: str = "us-east-1",
        timeout_seconds: int = 10,
        max_retries: int = 3,
    ) -> None:

        self._model_id = model_id
        self._max_retries = max_retries

        config = Config(
            read_timeout=timeout_seconds,
            connect_timeout=timeout_seconds,
            retries={"max_attempts": 1},  # We handle retries manually
        )

        self._client = boto3.client(
            service_name="bedrock-runtime",
            region_name=region_name,
            config=config,
        )

    # -----------------------------------------------------
    # Public API
    # -----------------------------------------------------

    def embed(self, texts: List[str]) -> List[List[float]]:
        """
        Convert list of texts into embeddings.
        Applies retry with exponential backoff.
        """

        embeddings: List[List[float]] = []

        for text in texts:
            vector = self._embed_with_retry(text)
            embeddings.append(vector)

        return embeddings

    # -----------------------------------------------------
    # Internal
    # -----------------------------------------------------

    def _embed_with_retry(self, text: str) -> List[float]:
        """
        Retry wrapper with exponential backoff.
        """

        attempt = 0
        backoff = 1

        while attempt < self._max_retries:
            try:
                response = self._client.invoke_model(
                    modelId=self._model_id,
                    contentType="application/json",
                    accept="application/json",
                    body=json.dumps({"inputText": text}),
                )

                response_body = json.loads(response["body"].read())

                embedding = response_body.get("embedding")

                if not embedding:
                    raise RuntimeError("Bedrock response missing 'embedding' field")

                return embedding

            except (ClientError, BotoCoreError, RuntimeError) as exc:
                attempt += 1

                if attempt >= self._max_retries:
                    raise RuntimeError(
                        f"Bedrock embedding failed after {self._max_retries} attempts"
                    ) from exc

                time.sleep(backoff)
                backoff *= 2  # exponential backoff