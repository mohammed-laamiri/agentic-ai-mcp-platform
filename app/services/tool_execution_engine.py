"""
Tool Execution Engine.

Coordinates execution of tools in a controlled, safe, and observable manner.

Step 7.4 adds:
- Structured observability hooks
- Latency measurement
- Trace correlation (run_id, call_id)
- Log-ready execution metadata
"""

from datetime import datetime, timezone
from typing import List, Set

from app.schemas.tool_call import ToolCall
from app.schemas.tool_result import ToolResult
from app.schemas.agent_execution_context import AgentExecutionContext
from app.services.tool_registry import ToolRegistry
from app.services.tool_executor import ToolExecutor


class ToolExecutionEngine:
    """
    Central execution coordinator for tools.

    HARD GUARANTEES:
    - One tool executes at a time
    - Same tool_call_id never executes twice
    - Execution order is deterministic
    - Every execution is observable
    """

    def __init__(self, tool_registry: ToolRegistry) -> None:
        self._executor = ToolExecutor(tool_registry=tool_registry)

    # --------------------------------------------------
    # Internal helpers
    # --------------------------------------------------

    def _init_context_state(self, context: AgentExecutionContext) -> None:
        """
        Initialize ephemeral execution state on context.
        """
        if not hasattr(context, "executed_tool_call_ids"):
            context.executed_tool_call_ids: Set[str] = set()  # type: ignore

        if not hasattr(context, "tool_results"):
            context.tool_results: List[ToolResult] = []  # type: ignore

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def execute_tool_call(
        self,
        tool_call: ToolCall,
        context: AgentExecutionContext,
    ) -> ToolResult:
        """
        Execute a single ToolCall with full observability.
        """
        self._init_context_state(context)

        # Ensure correlation ID
        if not tool_call.call_id:
            tool_call.call_id = f"{tool_call.tool_id}-{datetime.now(timezone.utc).timestamp()}"

        # Prevent duplicate execution
        if tool_call.call_id in context.executed_tool_call_ids:
            raise RuntimeError(
                f"ToolCall '{tool_call.call_id}' already executed in this run"
            )

        started_at = datetime.now(timezone.utc)

        # Execute tool using ToolExecutor
        result = self._executor.execute(tool_call=tool_call)

        finished_at = datetime.now(timezone.utc)
        latency_ms = int((finished_at - started_at).total_seconds() * 1000)

        # --------------------------------------------------
        # Observability metadata
        # --------------------------------------------------
        # Ensure metadata exists as a mutable dict
        if result.metadata is None:
            result.metadata = {}
        result.metadata.update(
            {
                "run_id": context.run_id,
                "tool_call_id": tool_call.call_id,
                "tool_id": tool_call.tool_id,
                "started_at": started_at.isoformat(),
                "finished_at": finished_at.isoformat(),
                "latency_ms": latency_ms,
                "status": "success" if result.success else "error",
            }
        )

        # Record execution
        context.executed_tool_call_ids.add(tool_call.call_id)
        context.tool_results.append(result)

        return result

    def execute_batch(
        self,
        tool_calls: List[ToolCall],
        context: AgentExecutionContext,
        fail_fast: bool = True,
    ) -> List[ToolResult]:
        """
        Execute tool calls sequentially with safety and observability.

        Args:
            tool_calls: List of tool calls to execute
            context: Execution-scoped context
            fail_fast: Stop execution on first failure
        """
        self._init_context_state(context)

        results: List[ToolResult] = []

        for tool_call in tool_calls:
            result = self.execute_tool_call(tool_call, context)
            results.append(result)

            if fail_fast and not result.success:
                break

        return results
