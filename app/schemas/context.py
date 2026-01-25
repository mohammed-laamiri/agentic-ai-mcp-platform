from pydantic import BaseModel, Field
from typing import Any, Dict, Optional
from uuid import uuid4


class ExecutionContext(BaseModel):
    """
    Shared context passed between agents and tools.

    This is a LONGER-LIVED context compared to AgentExecutionContext.

    It represents the execution environment for:
    - Session
    - Tools
    - Multi-agent orchestration
    - Memory access
    """

    execution_id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for this execution (correlation id)",
    )

    session_id: str = Field(
        ...,
        description="User session identifier",
    )

    user_id: Optional[str] = Field(
        default=None,
        description="User identifier (optional)",
    )

    strategy: Optional[str] = Field(
        default="SINGLE_AGENT",
        description="Execution strategy (SINGLE_AGENT, MULTI_AGENT, TOOL_CHAIN)",
    )

    tool_registry: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional reference to tool registry metadata",
    )

    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional execution metadata (correlation ids, flags, etc.)",
    )
