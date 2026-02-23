"""
Tool Execution Engine.

Coordinates validation and execution of tool calls.

Architectural role:
- Validates tool calls
- Resolves callable from ToolRegistry
- Executes tools safely using ToolExecutor
- Supports batch execution
- Integrates with ExecutionRuntime

IMPORTANT:
- Does NOT implement tool logic
- Delegates execution to ToolExecutor
"""

from typing import List, Optional, Callable, Any
from datetime import datetime, timezone

from app.schemas.tool_call import ToolCall
from app.schemas.tool_result import ToolResult
from app.schemas.agent_execution_context import AgentExecutionContext

from app.services.tool_registry import ToolRegistry
from app.services.tool_executor import ToolExecutor
from app.services.tool_validator import ToolValidator, ToolValidationError


class ToolExecutionEngine:
    """
    High-level engine responsible for validating and executing tools.

    Execution pipeline:

        ToolCall
           ↓
        Validator
           ↓
        Registry callable resolution
           ↓
        Executor
           ↓
        ToolResult
    """

    def __init__(self, tool_registry: ToolRegistry) -> None:
        self._tool_registry = tool_registry
        self._validator = ToolValidator(tool_registry)
        self._executor = ToolExecutor(tool_registry)

    # ==========================================================
    # Single tool execution
    # ==========================================================

    def execute(
        self,
        tool_call: ToolCall,
        context: Optional[AgentExecutionContext] = None,
        tool_fn: Optional[Callable[..., Any]] = None,
    ) -> ToolResult:
        start_time = datetime.now(timezone.utc)
        finished_time = start_time

        try:
            # -------------------------------
            # Step 1: Validate tool existence and arguments
            # -------------------------------
            self._validator.validate(tool_call)

            # -------------------------------
            # Step 2: Resolve callable
            # -------------------------------
            resolved_callable = tool_fn or self._tool_registry.get_callable(tool_call.tool_id)

            if resolved_callable is None:
                finished_time = datetime.now(timezone.utc)
                return ToolResult(
                    tool_call_id=getattr(tool_call, "call_id", None),
                    tool_id=tool_call.tool_id,
                    status="error",
                    output=None,
                    error=f"No callable registered for tool '{tool_call.tool_id}'",
                    started_at=start_time,
                    finished_at=finished_time,
                )

            # -------------------------------
            # Step 3: Execute via ToolExecutor
            # -------------------------------
            result = self._executor.execute(tool_call, tool_fn=resolved_callable)

            # Ensure all required fields exist for Pydantic
            if result.started_at is None:
                result.started_at = start_time
            if result.finished_at is None:
                result.finished_at = datetime.now(timezone.utc)
            if not hasattr(result, "status") or result.status is None:
                result.status = "success" if result.output is not None else "error"
            if not hasattr(result, "output"):
                result.output = None
            if not hasattr(result, "error"):
                result.error = None

            return result

        except ToolValidationError as exc:
            finished_time = datetime.now(timezone.utc)
            return ToolResult(
                tool_call_id=getattr(tool_call, "call_id", None),
                tool_id=tool_call.tool_id,
                status="error",
                output=None,
                error=str(exc),
                started_at=start_time,
                finished_at=finished_time,
            )

        except Exception as exc:
            finished_time = datetime.now(timezone.utc)
            return ToolResult(
                tool_call_id=getattr(tool_call, "call_id", None),
                tool_id=tool_call.tool_id,
                status="error",
                output=None,
                error=f"Execution engine failure: {str(exc)}",
                started_at=start_time,
                finished_at=finished_time,
            )

    # ==========================================================
    # Batch execution
    # ==========================================================

    def execute_batch(
        self,
        tool_calls: List[ToolCall],
        context: Optional[AgentExecutionContext] = None,
        fail_fast: bool = True,
    ) -> List[ToolResult]:
        results: List[ToolResult] = []

        for tool_call in tool_calls:
            result = self.execute(tool_call, context=context)
            results.append(result)
            if fail_fast and result.status == "error":
                break

        return results