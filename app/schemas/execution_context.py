from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.schemas.execution_trace import ExecutionEvent


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

    execution_trace: List[ExecutionEvent] = Field(
        default_factory=list,
        description="Trace of execution events for observability"
    )

    # ==================================================
    # Variables
    # ==================================================

    def get_variable(self, key: str, default: Optional[Any] = None) -> Any:
        """
        Safely get a variable from the runtime context.
        """
        return self.__dict__["variables"].get(key, default)

    def set_variable(self, key: str, value: Any) -> None:
        """
        Safely set a variable in the runtime context.
        """
        self.__dict__["variables"][key] = value

    # ==================================================
    # Agent Outputs
    # ==================================================

    def get_agent_output(self, agent_name: str, default: Optional[Any] = None) -> Any:
        return self.__dict__["agent_outputs"].get(agent_name, default)

    def set_agent_output(self, agent_name: str, value: Any) -> None:
        self.__dict__["agent_outputs"][agent_name] = value

    # ==================================================
    # Tool Outputs
    # ==================================================

    def get_tool_output(self, tool_name: str, default: Optional[Any] = None) -> Any:
        return self.__dict__["tool_outputs"].get(tool_name, default)

    def set_tool_output(self, tool_name: str, value: Any) -> None:
        self.__dict__["tool_outputs"][tool_name] = value

    # ==================================================
    # Execution Trace
    # ==================================================

    def add_trace_event(self, event: ExecutionEvent) -> None:
        """
        Append an execution event to the trace.
        """
        self.__dict__["execution_trace"].append(event)

    def get_execution_trace(self) -> List[ExecutionEvent]:
        """
        Return the full execution trace.
        """
        return list(self.__dict__["execution_trace"])
