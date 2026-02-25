from typing import Any, Dict, List, Optional
from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.tool_call import ToolCall
from app.schemas.tool_result import ToolResult


class ExecutionContext(BaseModel):
    """
    Runtime context shared across agents and tools
    during execution of an ExecutionPlan.

    This is NOT the plan itself.
    This is the evolving state while the plan runs.
    """

    task_id: str = Field(..., description="Associated task identifier")

    user_input: str = Field(..., description="Original user request")

    variables: Dict[str, Any] = Field(
        default_factory=dict,
        description="Shared mutable state across agents"
    )

    agent_outputs: Dict[str, Any] = Field(
        default_factory=dict,
        description="Outputs keyed by agent name"
    )

    tool_outputs: Dict[str, Any] = Field(
        default_factory=dict,
        description="Outputs keyed by tool name"
    )


# ==========================================================
# Persistence schemas (SAFE ADDITION)
# ==========================================================

class ExecutionContextCreate(BaseModel):
    """
    Persistable execution context snapshot.
    """

    task_id: str

    tool_calls: List[ToolCall] = Field(default_factory=list)

    tool_results: List[ToolResult] = Field(default_factory=list)

    final_output: Optional[str] = None

    execution_plan: Optional[Dict[str, Any]] = None


class ExecutionContextRead(ExecutionContextCreate):
    """
    Persisted execution context with metadata.
    """

    id: str

    created_at: datetime