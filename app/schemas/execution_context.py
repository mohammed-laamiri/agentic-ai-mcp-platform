"""
ExecutionContext Schema

Safe for FastAPI & Pydantic v2.
Captures runtime state for agents and tools.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, PrivateAttr


class ExecutionContext(BaseModel):
    """
    Runtime execution state container.

    Attributes:
        task_id: ID of the associated task
        user_input: Original user request
    """

    task_id: str
    user_input: str

    # Use Pydantic v2 private attributes for mutable dicts
    _variables: Dict[str, Any] = PrivateAttr(default_factory=dict)
    _agent_outputs: Dict[str, Any] = PrivateAttr(default_factory=dict)
    _tool_outputs: Dict[str, Any] = PrivateAttr(default_factory=dict)

    # -------------------------------
    # Helpers for easy manipulation
    # -------------------------------
    def set_variable(self, key: str, value: Any) -> None:
        """Set a variable in the execution context"""
        self._variables[key] = value

    def get_variable(self, key: str, default: Optional[Any] = None) -> Any:
        """Retrieve a variable value, returns default if not found"""
        return self._variables.get(key, default)

    def add_agent_output(self, agent_name: str, output: Any) -> None:
        """Store an agent's output"""
        self._agent_outputs[agent_name] = output

    def add_tool_output(self, tool_name: str, output: Any) -> None:
        """Store a tool's output"""
        self._tool_outputs[tool_name] = output

    # Optionally expose read-only views for serialization/logging
    @property
    def variables(self) -> Dict[str, Any]:
        return dict(self._variables)

    @property
    def agent_outputs(self) -> Dict[str, Any]:
        return dict(self._agent_outputs)

    @property
    def tool_outputs(self) -> Dict[str, Any]:
        return dict(self._tool_outputs)

    # Pydantic v2 ORM support
    model_config = {
        "from_attributes": True
    }
