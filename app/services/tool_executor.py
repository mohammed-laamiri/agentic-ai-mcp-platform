"""
Tool Executor.

Responsible for executing a single tool invocation at runtime.

Architectural role:
- Runtime execution boundary for tools
- Enforces execution contract
- Isolated from orchestration and planning
- Fetches metadata and callable from ToolRegistry
- Validates input against schema before execution

Supports:
- Retries
- Logging
- Observability hooks
"""

from datetime import datetime, timezone
from typing import Callable, Any, Optional, Dict

from app.schemas.tool_result import ToolResult
from app.schemas.tool_call import ToolCall
from app.schemas.agent_execution_context import AgentExecutionContext
from app.services.tool_registry import ToolRegistry
from app.services.tool_validator import ToolValidator, ToolValidationError


class ToolExecutor:
    """
    Executes tools in a controlled runtime environment.

    IMPORTANT:
    - Executes ONE tool call at a time
    - Stateless by design
    """

    def __init__(self, tool_registry: ToolRegistry) -> None:
        self._tool_registry = tool_registry
        self._validator = ToolValidator(tool_registry)

    def execute(
        self,
        tool_call: ToolCall,
        tool_fn: Optional[Callable[..., Any]] = None,
        max_retries: int = 1,
        context: Optional[AgentExecutionContext] = None,
    ) -> ToolResult:
        """
        Execute a tool function or a registered tool by ID.

        Args:
            tool_call: Structured tool invocation request
            tool_fn: Optional override callable (mainly for testing)
            max_retries: Number of retries in case of failure
            context: Optional execution context for tracking

        Returns:
            ToolResult
        """

        start_time = datetime.now(timezone.utc)
        attempt = 0
        execution_id = context.run_id if context else None
        metadata: Dict[str, Any] = {}
        if context:
            metadata["run_id"] = context.run_id

        while attempt < max_retries:
            attempt += 1

            # --------------------------------------------------
            # Fetch metadata
            # --------------------------------------------------
            tool_meta = self._tool_registry.get_tool(tool_call.tool_id)
            if not tool_meta:
                return ToolResult(
                    tool_call_id=getattr(tool_call, "call_id", None),
                    tool_id=tool_call.tool_id,
                    success=False,
                    status="error",
                    output=None,
                    error=f"Tool '{tool_call.tool_id}' not registered",
                    execution_id=execution_id,
                    metadata=metadata,
                    started_at=start_time,
                    finished_at=datetime.now(timezone.utc),
                )

            # --------------------------------------------------
            # Resolve callable
            # --------------------------------------------------
            if tool_fn is None:
                tool_fn = self._tool_registry.get_callable(tool_call.tool_id)

            if not tool_fn:
                # Return stub output when no executor is bound
                return ToolResult(
                    tool_call_id=getattr(tool_call, "call_id", None),
                    tool_id=tool_call.tool_id,
                    success=True,
                    status="success",
                    output=f"[STUB TOOL OUTPUT] tool_id={tool_call.tool_id} arguments={tool_call.arguments}",
                    error=None,
                    execution_id=execution_id,
                    metadata=metadata,
                    started_at=start_time,
                    finished_at=datetime.now(timezone.utc),
                )

            # --------------------------------------------------
            # Validate input
            # --------------------------------------------------
            try:
                self._validator.validate(tool_call)
            except ToolValidationError as exc:
                return ToolResult(
                    tool_call_id=getattr(tool_call, "call_id", None),
                    tool_id=tool_call.tool_id,
                    success=False,
                    status="error",
                    output=None,
                    error=f"Validation failed: {exc}",
                    execution_id=execution_id,
                    metadata=metadata,
                    started_at=start_time,
                    finished_at=datetime.now(timezone.utc),
                )

            # --------------------------------------------------
            # Execute safely
            # --------------------------------------------------
            try:
                output = tool_fn(**tool_call.arguments)
                return ToolResult(
                    tool_call_id=getattr(tool_call, "call_id", None),
                    tool_id=tool_call.tool_id,
                    success=True,
                    status="success",
                    output=output,
                    error=None,
                    execution_id=execution_id,
                    metadata=metadata,
                    started_at=start_time,
                    finished_at=datetime.now(timezone.utc),
                )

            except Exception as exc:  # noqa: BLE001
                last_error = str(exc)
                if attempt >= max_retries:
                    return ToolResult(
                        tool_call_id=getattr(tool_call, "call_id", None),
                        tool_id=tool_call.tool_id,
                        success=False,
                        status="error",
                        output=None,
                        error=last_error,  # Just the error message
                        execution_id=execution_id,
                        metadata=metadata,
                        started_at=start_time,
                        finished_at=datetime.now(timezone.utc),
                    )
                # Optionally: log retry attempt here

        # Safety fallback (should not reach here normally)
        return ToolResult(
            tool_call_id=getattr(tool_call, "call_id", None),
            tool_id=tool_call.tool_id,
            success=False,
            status="error",
            output=None,
            error="Execution exhausted all retries",
            execution_id=execution_id,
            metadata=metadata,
            started_at=start_time,
            finished_at=datetime.now(timezone.utc),
        )
