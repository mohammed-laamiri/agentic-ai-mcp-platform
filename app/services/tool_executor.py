"""
Tool Executor (MCP).

Responsible for executing a single tool invocation at runtime.

Adds:
- MCP ToolResult normalization
- Execution ID
- Retries
- Structured metadata
- Optional integration with AgentExecutionContext
"""

from datetime import datetime, timezone
from typing import Callable, Any, Optional
from uuid import uuid4

from app.schemas.tool_call import ToolCall
from app.schemas.tool_result import ToolResult
from app.services.tool_registry import ToolRegistry, ToolMetadata
from app.schemas.agent_execution_context import AgentExecutionContext


class ToolExecutor:
    """
    Executes a single tool in a controlled runtime environment.

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
        context: Optional[AgentExecutionContext] = None,
        tool_fn: Optional[Callable[..., Any]] = None,
        retries: int = 0,
    ) -> ToolResult:
        """
        Execute a tool function or a registered tool by ID.

        Args:
            tool_call: Structured tool invocation request
            context: Optional execution context for observability
            tool_fn: Optional Python callable implementing the tool
            retries: Number of retries attempted

        Returns:
            ToolResult: MCP-compliant execution result
        """

        start_time = datetime.now(timezone.utc)

        # Fetch tool metadata
        tool_meta: Optional[ToolMetadata] = self._tool_registry.get_tool(tool_call.tool_id)
        if tool_meta is None:
            return ToolResult(
                tool_call_id=tool_call.call_id,
                tool_id=tool_call.tool_id,
                success=False,
                output=None,
                error=f"Tool '{tool_call.tool_id}' not registered",
                metadata={},
                execution_id=tool_call.call_id or str(uuid4()),
                retries=retries,
            )

        # Determine callable
        if tool_fn is None:
            # Default stub execution
            def tool_fn_stub(**kwargs: Any) -> str:
                return f"[STUB TOOL OUTPUT] Tool '{tool_meta.name}' executed with input: {kwargs}"
            tool_fn = tool_fn_stub

        # Execute safely
        try:
            output = tool_fn(**tool_call.arguments)
            success = True
            error = None
        except Exception as exc:  # noqa: BLE001
            output = None
            success = False
            error = str(exc)

        finished_time = datetime.now(timezone.utc)

        # Build metadata
        metadata = {
            "tool_name": getattr(tool_meta, "name", None),
            "version": getattr(tool_meta, "version", None),
            "started_at": start_time.isoformat(),
            "finished_at": finished_time.isoformat(),
        }

        # Optional: attach run context
        if context:
            metadata["run_id"] = context.run_id

        return ToolResult(
            tool_call_id=tool_call.call_id,
            tool_id=tool_call.tool_id,
            success=success,
            output=output,
            error=error,
            metadata=metadata,
            execution_id=tool_call.call_id or str(uuid4()),
            retries=retries,
        )
