"""
Tool Validator.

Responsible for validating tool calls BEFORE execution.

Validation layers:
1. Tool existence
2. Argument schema validation
"""

from typing import Dict, Any

from app.schemas.tool_call import ToolCall
from app.services.tool_registry import ToolRegistry


class ToolValidationError(Exception):
    pass


class ToolValidator:

    def __init__(self, registry: ToolRegistry):
        self._registry = registry

    def validate(self, tool_call: ToolCall) -> None:
        """
        Validate tool call against registry schema.
        """

        # --------------------------------------------------
        # Tool existence
        # --------------------------------------------------

        if not self._registry.has_tool(tool_call.tool_id):
            raise ToolValidationError(
                f"Tool '{tool_call.tool_id}' is not registered"
            )

        # --------------------------------------------------
        # Schema validation
        # --------------------------------------------------

        schema = self._registry.get_input_schema(tool_call.tool_id)

        if not schema:
            return

        self._validate_arguments(
            tool_call.tool_id,
            tool_call.arguments,
            schema,
        )

    # --------------------------------------------------

    def _validate_arguments(
        self,
        tool_id: str,
        arguments: Dict[str, Any],
        schema: Dict[str, Any],
    ) -> None:

        required = schema.get("required", [])
        properties = schema.get("properties", {})

        # Required check
        for field in required:
            if field not in arguments:
                raise ToolValidationError(
                    f"Tool '{tool_id}' missing required argument '{field}'"
                )

        # Type check
        for field, value in arguments.items():

            expected = properties.get(field)

            if not expected:
                continue

            expected_type = expected.get("type")

            if expected_type == "string" and not isinstance(value, str):
                raise ToolValidationError(
                    f"Argument '{field}' must be string"
                )

            if expected_type == "integer" and not isinstance(value, int):
                raise ToolValidationError(
                    f"Argument '{field}' must be integer"
                )

            if expected_type == "number" and not isinstance(value, (int, float)):
                raise ToolValidationError(
                    f"Argument '{field}' must be number"
                )

            if expected_type == "boolean" and not isinstance(value, bool):
                raise ToolValidationError(
                    f"Argument '{field}' must be boolean"
                )

            if expected_type == "object" and not isinstance(value, dict):
                raise ToolValidationError(
                    f"Argument '{field}' must be object"
                )