"""
Execution Context.

Runtime context shared across agents and tools
during execution of an ExecutionPlan.

This is NOT the plan itself.
This is the evolving state while the plan runs.

Architectural intent:
- Created by Orchestrator
- Passed across agents and tools
- Holds shared state, outputs, and variables
"""

from typing import Any, Dict, Optional
from typing_extensions import Annotated
from pydantic import BaseModel, Field


class ExecutionContext(BaseModel):
    """
    Runtime execution state container.

    Used for:
    - Variable passing between agents
    - Capturing agent outputs
    - Capturing tool outputs
    """

    task_id: str = Field(..., description="Associated task identifier")
    user_input: str = Field(..., description="Original user request")

    variables: Annotated[
        Dict[str, Any],
        Field(default_factory=dict, description="Shared mutable variables across agents"),
    ]

    agent_outputs: Annotated[
        Dict[str, Any],
        Field(default_factory=dict, description="Outputs keyed by agent name"),
    ]

    tool_outputs: Annotated[
        Dict[str, Any],
        Field(default_factory=dict, description="Outputs keyed by tool name"),
    ]

    # -------------------------------------------------
    # Helpers (non-breaking)
    # -------------------------------------------------

    def set_variable(self, key: str, value: Any) -> None:
        """
        Store a shared variable.
        """
        self.variables[key] = value

    def get_variable(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Retrieve a shared variable.
        """
        return self.variables.get(key, default)

    def add_agent_output(self, agent_name: str, output: Any) -> None:
        """
        Store output from an agent.
        """
        self.agent_outputs[agent_name] = output

    def add_tool_output(self, tool_name: str, output: Any) -> None:
        """
        Store output from a tool.
        """
        self.tool_outputs[tool_name] = output
