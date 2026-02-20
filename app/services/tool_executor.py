"""
Tool Executor.

Responsible for executing a single tool invocation at runtime.
"""

from datetime import datetime, timezone
from typing import Callable, Any, Optional

from app.schemas.tool_result import ToolResult
from app.schemas.tool_call import ToolCall
from app.services.tool_registry import ToolRegistry


class ToolExecutor:
    """
    Executes tools in a controlled runtime environment.
    """

    def __init__(self, tool_registry: ToolRegistry) -> None:
        self._tool_registry = tool_registry

    def execute(
        self,
        tool_call: ToolCall,
        tool_fn: Optional[Callable[..., Any]] = None,
    ) -> ToolResult:
        """
        Execute a tool function or a registered tool by ID.
        """

        start_time = datetime.now(timezone.utc)

        # Fetch metadata
        tool_meta = self._tool_registry.get_tool(tool_call.tool_id)
        if tool_meta is None:
            return ToolResult(
                tool_call_id=getattr(tool_call, "call_id", None),
                tool_id=tool_call.tool_id,
                status="error",
                output=None,
                error=f"Tool '{tool_call.tool_id}' not registered",
                started_at=start_time,
                finished_at=datetime.now(timezone.utc),
            )

        # Resolve callable
        if tool_fn is None:
            tool_fn = self._tool_registry.get_callable(tool_call.tool_id)

        if tool_fn is None:
            return ToolResult(
                tool_call_id=getattr(tool_call, "call_id", None),
                tool_id=tool_call.tool_id,
                status="error",
                output=None,
                error=f"No execution binding found for tool '{tool_call.tool_id}'",
                started_at=start_time,
                finished_at=datetime.now(timezone.utc),
            )

        # Execute safely
        try:
            output = tool_fn(**tool_call.arguments)
            status = "success"
            error = None
        except Exception as exc:
            output = None
            status = "error"
            error = str(exc)

        finished_time = datetime.now(timezone.utc)

        return ToolResult(
            tool_call_id=getattr(tool_call, "call_id", None),
            tool_id=tool_call.tool_id,
            status=status,
            output=output,
            error=error,
            started_at=start_time,
            finished_at=finished_time,
        )