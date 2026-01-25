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

from typing import Optional, Dict, Any, List
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

    task_id: Optional[str] = Field(
        default=None,
        description="Associated task identifier",
    )

    agent_id: Optional[str] = Field(
        default=None,
        description="ID of the agent that executed the task",
    )

    agent_name: Optional[str] = Field(
        default=None,
        description="Human-readable agent name",
    )

    strategy: Optional[str] = Field(
        default="SINGLE_AGENT",
        description="Execution strategy used",
    )

    input: Optional[str] = Field(
        default=None,
        description="Input provided to the agent",
    )

    output: Optional[str] = Field(
        default=None,
        description="Final output produced by the agent",
    )

    status: str = Field(
        default="SUCCESS",
        description="Execution status (SUCCESS | FAILED | PARTIAL)",
    )

    tool_calls: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="Tools invoked during execution",
    )

    errors: Optional[List[str]] = Field(
        default=None,
        description="Errors encountered during execution",
    )

    child_results: Optional[List["ExecutionResult"]] = Field(
        default=None,
        description="Child execution results (for MULTI_AGENT)",
    )

    metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional execution metadata (tokens, costs, etc.)",
    )

    started_at: Optional[datetime] = Field(
        default=None,
        description="Execution start time (UTC)",
    )

    finished_at: Optional[datetime] = Field(
        default=None,
        description="Execution finish time (UTC)",
    )

    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Execution creation timestamp (UTC)",
    )

    class Config:
        arbitrary_types_allowed = True
