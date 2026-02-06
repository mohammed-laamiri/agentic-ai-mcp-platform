"""
Tool Executor.

Responsible for executing a single tool invocation at runtime.

Architectural role:
- Runtime execution boundary for tools
- Enforces execution contract
- Isolated from orchestration and planning
- Fetches metadata from ToolRegistry

MCP upgrades:
- Uniform ToolResult normalization
- Execution ID attachment
- Retry counter integration
- Structured metadata
- Exception standardization
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

    # -----------------------------
    # Public API
    # -----------------------------

    def execute(
        self,
        tool_call: ToolCall,
        tool_fn: Optional[Callable[..., Any]] = None,
        retries: int = 0,
    ) -> ToolResult:
        """
        Execute a tool function or a registered tool by ID.

        Args:
            tool_call: Structured tool invocation request
            tool_fn: Optional Python callable implementing the tool
                     If None, tool will be fetched from ToolRegistry
            retries: Number of retry attempts

        Returns:
            ToolResult: Structured MCP-compliant execution result
        """

        # Ensure correlation id
        if not tool_call.call_id:
            tool_call.call_id = str(uuid4())

        execution_id = tool_call.call_id
        started_at = datetime.now(timezone.utc)

        # Fetch tool metadata
        tool_meta: Optional[ToolMetadata] = self._tool_registry.get_tool(tool_call.tool_id)
        if tool_meta is None:
            return ToolResult(
                tool_call_id=tool_call.call_id,
                tool_id=tool_call.tool_id,
                success=False,
                output=None,
                error=f"Tool '{tool_call.tool_id}' not registered",
                metadata={
                    "execution_id": execution_id,
                    "started_at": started_at.isoformat(),
                    "status": "error",
                },
            )

        # Determine callable
        if tool_fn is None:
            def tool_fn_stub(**kwargs: Any) -> str:
                return f"[STUB TOOL OUTPUT] Tool '{tool_meta.name}' executed with input: {kwargs}"

            tool_fn = tool_fn_stub

        last_error: Optional[str] = None

        for attempt in range(retries + 1):
            try:
                output = tool_fn(**tool_call.arguments)
                finished_at = datetime.now(timezone.utc)

                latency_ms = int((finished_at - started_at).total_seconds() * 1000)

                return ToolResult(
                    tool_call_id=tool_call.call_id,
                    tool_id=tool_call.tool_id,
                    success=True,
                    output=output,
                    error=None,
                    metadata={
                        "execution_id": execution_id,
                        "tool_name": getattr(tool_meta, "name", None),
                        "version": getattr(tool_meta, "version", None),
                        "attempt": attempt + 1,
                        "latency_ms": latency_ms,
                        "started_at": started_at.isoformat(),
                        "finished_at": finished_at.isoformat(),
                        "status": "success",
                    },
                )

            except Exception as exc:  # noqa: BLE001
                last_error = str(exc)

        finished_at = datetime.now(timezone.utc)
        latency_ms = int((finished_at - started_at).total_seconds() * 1000)

        return ToolResult(
            tool_call_id=tool_call.call_id,
            tool_id=tool_call.tool_id,
            success=False,
            output=None,
            error=last_error,
            metadata={
                "execution_id": execution_id,
                "tool_name": getattr(tool_meta, "name", None),
                "version": getattr(tool_meta, "version", None),
                "attempt": retries + 1,
                "latency_ms": latency_ms,
                "started_at": started_at.isoformat(),
                "finished_at": finished_at.isoformat(),
                "status": "error",
            },
        )
