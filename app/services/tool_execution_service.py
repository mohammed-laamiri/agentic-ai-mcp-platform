"""
Tool execution service.

Responsible for:
- Executing ToolCall contracts
- Returning ToolResult objects
- Acting as the ONLY runtime that touches tools

IMPORTANT:
- No orchestration logic
- No agent logic
- Pure execution layer
"""

from datetime import datetime, timezone
from typing import Dict

from app.schemas.tool_call import ToolCall
from app.schemas.tool_result import ToolResult


class ToolExecutionService:
    """
    Executes tools based on ToolCall contracts.

    Architectural role:
    - Runtime boundary for tools
    - Enforces isolation from agents & orchestrator
    """

    def __init__(self) -> None:
        """
        Initialize tool registry.

        Later:
        - Dynamic registry
        - MCP adapters
        - Permission checks
        """
        self._tool_registry: Dict[str, callable] = {
            "stub_tool_1": self._stub_tool,
        }

    # ==================================================
    # Public API
    # ==================================================

    def execute(self, tool_call: ToolCall) -> ToolResult:
        """
        Execute a single tool call.

        Always returns ToolResult (never raises to caller).
        """
        tool_fn = self._tool_registry.get(tool_call.tool_id)

        if not tool_fn:
            return ToolResult(
                tool_id=tool_call.tool_id,
                success=False,
                error=f"Tool '{tool_call.tool_id}' not found",
            )

        try:
            output = tool_fn(**tool_call.arguments)

            return ToolResult(
                tool_id=tool_call.tool_id,
                success=True,
                output=output,
                metadata={
                    "executed_at": datetime.now(timezone.utc).isoformat(),
                },
            )

        except Exception as exc:
            return ToolResult(
                tool_id=tool_call.tool_id,
                success=False,
                error=str(exc),
            )

    # ==================================================
    # Stub tools (temporary)
    # ==================================================

    def _stub_tool(self, input_text: str) -> dict:
        """
        Example stub tool.

        This will be replaced by:
        - Real API calls
        - MCP tools
        - External services
        """
        return {
            "echo": input_text,
            "length": len(input_text),
        }
