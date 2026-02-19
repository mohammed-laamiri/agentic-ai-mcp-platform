"""
Tool Execution Engine (MCP + Observability).

Responsible for executing tools declared via ToolCall.

Adds:
- Span IDs
- Parent/child tracing
- Pre/Post hooks
- Timeout-ready structure
- Structured metadata events
"""

import time
from typing import List, Callable, Optional
from uuid import uuid4

from app.schemas.tool_call import ToolCall
from app.schemas.tool_result import ToolResult
from app.schemas.agent_execution_context import AgentExecutionContext
from app.services.tool_registry import ToolRegistry
from app.services.tool_executor import ToolExecutor


class ToolExecutionEngine:
    """
    Runtime executor for registered MCP tools with observability.
    """

    def __init__(self, tool_registry: ToolRegistry) -> None:
        self._tool_registry = tool_registry
        self._executor = ToolExecutor(tool_registry)

        # Hooks
        self._pre_hooks: List[Callable[[ToolCall, AgentExecutionContext], None]] = []
        self._post_hooks: List[Callable[[ToolResult, AgentExecutionContext], None]] = []

    # ==================================================
    # Hooks
    # ==================================================

    def register_pre_hook(self, hook: Callable[[ToolCall, AgentExecutionContext], None]) -> None:
        self._pre_hooks.append(hook)

    def register_post_hook(self, hook: Callable[[ToolResult, AgentExecutionContext], None]) -> None:
        self._post_hooks.append(hook)

    # ==================================================
    # Execution
    # ==================================================

    def execute_batch(
        self,
        tool_calls: List[ToolCall],
        context: AgentExecutionContext,
        fail_fast: bool = True,
        retries: int = 0,
        timeout: Optional[float] = None,  # placeholder
    ) -> List[ToolResult]:
        """
        Execute a batch of tool calls sequentially with observability.
        """
        results: List[ToolResult] = []

        for call in tool_calls:
            self._apply_pre_hooks(call, context)

            # Execute via ToolExecutor
            result = self._executor.execute(
                tool_call=call,
                context=context,
                retries=retries,
            )

            # Span and latency metadata
            latency = time.time() - time.time()
            span_id = str(uuid4())

            # Ensure metadata is mutable
            if result.metadata is None:
                result.metadata = {}

            result.metadata.update(
                {
                    "span_id": span_id,
                    "parent_run_id": context.run_id,
                    "latency_total": latency,
                }
            )

            self._apply_post_hooks(result, context)

            results.append(result)
            context.add_tool_result(result)

            if fail_fast and not result.success:
                break

        return results

    # ==================================================
    # Internal helpers
    # ==================================================

    def _apply_pre_hooks(self, call: ToolCall, context: AgentExecutionContext) -> None:
        for hook in self._pre_hooks:
            hook(call, context)

    def _apply_post_hooks(self, result: ToolResult, context: AgentExecutionContext) -> None:
        for hook in self._post_hooks:
            hook(result, context)
