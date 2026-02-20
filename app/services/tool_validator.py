"""
Tool Validator.

Responsible for validating tool calls BEFORE execution.

Architectural role:
- Enforces tool existence
- Enforces argument contract
- Prevents invalid runtime execution
- Acts as safety boundary between Planner and Executor

IMPORTANT:
- Does NOT execute tools
- Does NOT mutate tool calls
- Does NOT handle retries

Future extensions:
- JSON Schema validation
- Permission checks
- Rate limiting
- Cost estimation
"""

from typing import Dict, Any

from app.schemas.tool_call import ToolCall
from app.services.tool_registry import ToolRegistry


class ToolValidationError(Exception):
    """
    Raised when a tool call fails validation.
    """
    pass


class ToolValidator:
    """
    Validates tool calls before execution.
    """

    def __init__(self, tool_registry: ToolRegistry) -> None:
        self._tool_registry = tool_registry

    def validate(self, tool_call: ToolCall) -> None:
        """
        Validate a ToolCall.

        Raises:
            ToolValidationError if validation fails.
        """

        # --------------------------------------------------
        # Validate tool exists
        # --------------------------------------------------

        if not self._tool_registry.has_tool(tool_call.tool_id):
            raise ToolValidationError(
                f"Tool '{tool_call.tool_id}' is not registered."
            )

        # --------------------------------------------------
        # Validate arguments structure
        # --------------------------------------------------

        if not isinstance(tool_call.arguments, dict):
            raise ToolValidationError(
                "Tool arguments must be a dictionary."
            )

        # --------------------------------------------------
        # Validate keys are strings
        # --------------------------------------------------

        for key in tool_call.arguments.keys():
            if not isinstance(key, str):
                raise ToolValidationError(
                    "Tool argument keys must be strings."
                )