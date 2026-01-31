"""
Tool Executor.

Responsible for executing a single tool invocation at runtime.

Architectural role:
- Runtime execution boundary for tools
- Enforces execution contract
- Isolated from orchestration and planning

This will later support:
- Timeouts
- Retries
- Sandboxing
- Cost tracking
- Observability hooks
"""

from datetime import datetime, timezone
from typing import Callable, Any
from uuid import uuid4

from app.schemas.tool_result import ToolResult
from app.schemas.tool_call import ToolCall


class ToolExecutor:
    """
    Executes tools in a controlled runtime environment.

    IMPORTANT:
    - Executes ONE tool call at a time
    - Stateless by design
    """

    def execute(
        self,
        tool_fn: Callable[..., Any],
        tool_call: ToolCall,
    ) -> ToolResult:
        """
        Execute a tool function.

        Args:
            tool_fn: The actual callable implementing the tool
            tool_call: Structured tool invocation request

        Returns:
            ToolResult: Structured execution result
        """

        start_time = datetime.now(timezone.utc)

        try:
            output = tool_fn(**tool_call.arguments)

            return ToolResult(
                tool_call_id=tool_call.tool_call_id,
                tool_id=tool_call.tool_id,
                status="success",
                output=output,
                error=None,
                started_at=start_time,
                finished_at=datetime.now(timezone.utc),
            )

        except Exception as exc:  # noqa: BLE001 (intentional boundary)
            return ToolResult(
                tool_call_id=tool_call.tool_call_id,
                tool_id=tool_call.tool_id,
                status="error",
                output=None,
                error=str(exc),
                started_at=start_time,
                finished_at=datetime.now(timezone.utc),
            )
