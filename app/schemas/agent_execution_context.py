"""
Agent Execution Context.

This module defines the execution-scoped context object used during
a single orchestrator `/run` invocation.

Architectural intent:
- This context is CREATED by the Orchestrator
- It is READ-ONLY for agents
- It represents ONE execution run (ephemeral)

This is intentionally separate from `ExecutionContext`:
- ExecutionContext (existing):
    - Session / tool / MCP oriented
    - Longer-lived
- AgentExecutionContext (this file):
    - Orchestration-run oriented
    - Short-lived
    - Coordination and tracing focused

Current responsibilities:
- Carry execution metadata
- Provide a stable threading object between orchestration steps

Future responsibilities (by design, not implemented yet):
- MCP context root
- Memory write hooks
- Retry / reflection metadata
- Observability correlation
"""

from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, Field


class AgentExecutionContext(BaseModel):
    """
    Execution-scoped context for a single agent run.

    IMPORTANT:
    - Agents must treat this as READ-ONLY
    - No agent should mutate this object
    """

    run_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for this execution run",
    )

    started_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when orchestration began",
    )

    # NOTE:
    # Intentionally minimal for now.
    # We are creating a load-bearing abstraction without
    # prematurely filling it with responsibilities.
