"""
Agent Execution Context.

Execution-scoped context object used during
a single orchestrator run.

Architectural intent:
- Created by the Orchestrator
- Read-only for agents
- Collects execution metadata
"""

from datetime import datetime
from typing import List
from uuid import uuid4

from pydantic import BaseModel, Field, PrivateAttr

from app.schemas.tool_call import ToolCall
from app.schemas.rag.chunk import Chunk


class AgentExecutionContext(BaseModel):
    """
    Execution-scoped context for a single orchestration run.

    IMPORTANT:
    - Agents must treat this as READ-ONLY
    - Orchestrator owns mutation
    """

    run_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for this execution run",
    )

    started_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when orchestration began",
    )

    tool_calls: List[ToolCall] = Field(
        default_factory=list,
        description="Tool calls declared by agents during execution",
    )

    # ==================================================
    # Private runtime attributes
    # ==================================================

    _retrieved_chunks: List[Chunk] = PrivateAttr(default_factory=list)

    # ==================================================
    # Public accessors
    # ==================================================

    @property
    def retrieved_chunks(self) -> List[Chunk]:
        """
        Access the chunks retrieved via RAG for this execution.
        Agents should treat this as read-only.
        """
        return self._retrieved_chunks

    def add_retrieved_chunks(self, chunks: List[Chunk]) -> None:
        """
        Add RAG-retrieved chunks to this execution context.
        """
        self._retrieved_chunks.extend(chunks)

    def clear_retrieved_chunks(self) -> None:
        """
        Clear retrieved chunks. Useful for retries or new queries.
        """
        self._retrieved_chunks.clear()
