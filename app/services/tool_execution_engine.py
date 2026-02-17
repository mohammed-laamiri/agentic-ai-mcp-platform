"""
Tool Executor.

Responsible for executing a single tool invocation at runtime.

Architectural role:
- Runtime execution boundary for tools
- Enforces execution contract
- Isolated from orchestration and planning
- Fetches metadata from ToolRegistry

This will later support:
- Timeouts
- Retries
- Sandboxing
- Cost tracking
- Observability hooks
"""

from datetime import datetime, timezone
from typing import Callable, Any, Optional
from uuid import uuid4

from app.schemas.tool_result import ToolResult
from app.schemas.tool_call import ToolCall
from app.services.tool_registry import ToolRegistry, ToolMetadata


class ToolExecutor:
    """
    Executes tools in a controlled runtime environment.

    IMPORTANT:
    - Executes ONE tool call at a time
    - Stateless by design
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

        Args:
            tool_call: Structured tool invocation request
            tool_fn: Optional Python callable implementing the tool
                     If None, tool will be fetched from ToolRegistry

        Returns:
            ToolResult: Structured execution result
        """

        start_time = datetime.now(timezone.utc)

        # Fetch tool metadata
        tool_meta: Optional[ToolMetadata] = self._tool_registry.get_tool(tool_call.tool_id)
        if tool_meta is None:
            return ToolResult(
                tool_call_id=tool_call.tool_call_id,
                tool_id=tool_call.tool_id,
                status="error",
                output=None,
                error=f"Tool '{tool_call.tool_id}' not registered",
                started_at=start_time,
                finished_at=datetime.now(timezone.utc),
            )

        # Determine callable
        if tool_fn is None:
            # For now, we assume stub execution (to be replaced later)
            def tool_fn_stub(**kwargs: Any) -> str:
                return f"[STUB TOOL OUTPUT] Tool '{tool_meta.name}' executed with input: {kwargs}"
            tool_fn = tool_fn_stub

        try:
            output = tool_fn(**tool_call.arguments)
            status = "success"
            error = None

        except Exception as exc:  # noqa: BLE001
            output = None
            status = "error"
            error = str(exc)

        finished_time = datetime.now(timezone.utc)

        return ToolResult(
            tool_call_id=tool_call.tool_call_id,
            tool_id=tool_call.tool_id,
            status=status,
            output=output,
            error=error,
            started_at=start_time,
            finished_at=finished_time,
        )
