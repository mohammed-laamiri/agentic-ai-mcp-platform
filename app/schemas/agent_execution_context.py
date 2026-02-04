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

from pydantic import BaseModel, Field

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

    retrieved_chunks: List[Chunk] = Field(
        default_factory=list,
        description="Knowledge chunks retrieved via RAG for this execution",
    )

    # Intentionally minimal.
    # This is a load-bearing abstraction.
