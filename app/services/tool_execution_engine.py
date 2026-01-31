"""
Tool Execution Engine.

Coordinates execution of tools in a controlled, safe manner.

Architectural role:
- Receives ToolCall objects from agents (via Orchestrator)
- Executes them via ToolExecutor
- Collects ToolResult objects
- Maintains execution metadata for observability

Future extensions:
- Parallel execution
- Retry / timeout policies
- Permission enforcement
- Cost and rate tracking
"""

from datetime import datetime, timezone
from typing import List, Optional

from app.schemas.tool_call import ToolCall
from app.schemas.tool_result import ToolResult
from app.schemas.agent_execution_context import AgentExecutionContext
from app.services.tool_registry import ToolRegistry
from app.services.tool_executor import ToolExecutor


class ToolExecutionEngine:
    """
    Central execution coordinator for tools.
    """

    def __init__(self, tool_registry: ToolRegistry) -> None:
        self._tool_registry = tool_registry
        self._executor = ToolExecutor(tool_registry=tool_registry)

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def execute_tool_call(
        self,
        tool_call: ToolCall,
        context: Optional[AgentExecutionContext] = None,
    ) -> ToolResult:
        """
        Execute a single ToolCall and optionally store result in context.

        Args:
            tool_call: The tool invocation request.
            context: Optional execution context to store results.

        Returns:
            ToolResult: The structured execution outcome.
        """
        start_time = datetime.now(timezone.utc)

        # Assign a call_id if missing for tracing
        if not tool_call.call_id:
            tool_call.call_id = f"{tool_call.tool_id}-{start_time.timestamp()}"

        # Execute via ToolExecutor
        result = self._executor.execute(tool_call=tool_call)

        # Collect metadata for observability
        result.metadata["executed_at"] = start_time.isoformat()

        # Store in execution context if provided
        if context is not None:
            if not hasattr(context, "tool_results"):
                context.tool_results = []  # type: ignore
            context.tool_results.append(result)  # type: ignore

        return result

    def execute_batch(
        self,
        tool_calls: List[ToolCall],
        context: Optional[AgentExecutionContext] = None,
        fail_fast: bool = True,
    ) -> List[ToolResult]:
        """
        Execute a batch of ToolCalls sequentially.

        Args:
            tool_calls: List of tool invocation requests.
            context: Optional execution context to store results.
            fail_fast: Stop execution on first failure if True.

        Returns:
            List[ToolResult]: Execution outcomes for each call.
        """
        results: List[ToolResult] = []

        for call in tool_calls:
            result = self.execute_tool_call(call, context=context)
            results.append(result)

            if fail_fast and not result.success:
                break  # Stop on first failure

        return results
