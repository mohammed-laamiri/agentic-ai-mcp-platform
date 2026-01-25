from typing import Any, Dict
from pydantic import BaseModel, Field


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
