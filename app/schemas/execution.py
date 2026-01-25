"""
Execution result schema.

Represents the structured output produced by an agent execution.

This model is intentionally minimal for now and will evolve to support:
- Tool calls
- Multi-step reasoning
- Traces and logs
- Token usage
- Error states
"""

from typing import Optional, Dict, Any
from datetime import datetime

from pydantic import BaseModel, Field


class ExecutionResult(BaseModel):
    """
    Domain-level execution result.

    Contract between:
    - AgentService
    - OrchestratorService
    - TaskService
    """

    execution_id: str = Field(
        ...,
        description="Unique execution identifier",
    )

    agent_id: str = Field(
        ...,
        description="ID of the agent that executed the task",
    )

    agent_name: str = Field(
        ...,
        description="Human-readable agent name",
    )

    input: Optional[str] = Field(
        default=None,
        description="Input provided to the agent",
    )

    output: Optional[str] = Field(
        default=None,
        description="Final output produced by the agent",
    )

    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional execution metadata (tokens, tools, etc.)",
    )

    timestamp: datetime = Field(
        ...,
        description="Execution timestamp (UTC)",
    )
