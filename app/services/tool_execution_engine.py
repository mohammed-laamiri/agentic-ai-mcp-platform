"""
Tool Execution Engine.

Responsible for executing tools declared via ToolCall.

Architectural role:
- Validates tool existence
- Dispatches execution
- Captures MCP-style ToolResult contracts
- Supports retries and fail-fast semantics

IMPORTANT:
- Does NOT plan tools
- Does NOT reason
- Only executes
"""

import time
from datetime import datetime, timezone
from typing import Callable, Dict, List, Set

from app.schemas.tool_call import ToolCall
from app.schemas.tool_result import ToolResult
from app.schemas.agent_execution_context import AgentExecutionContext
from app.services.tool_registry import ToolRegistry


class ToolExecutionEngine:
    """
    Runtime executor for registered tools.
    """

    def __init__(self, tool_registry: ToolRegistry) -> None:
        self._tool_registry = tool_registry
        self._executors: Dict[str, Callable[..., object]] = {}

    # ==================================================
    # Registration
    # ==================================================

    def register_executor(self, tool_id: str, handler: Callable[..., object]) -> None:
        """
        Register a callable executor for a tool.

        handler(**kwargs) -> Any
        """
        self._executors[tool_id] = handler

    # ==================================================
    # Internal helpers
    # ==================================================

    def _init_context_state(self, context: AgentExecutionContext) -> None:
        """
        Initialize ephemeral execution state on context safely.
        """
        if not hasattr(context, "tool_results"):
            context.tool_results: List[ToolResult] = []  # type: ignore

        if not hasattr(context, "executed_tool_call_ids"):
            context.executed_tool_call_ids: Set[str] = set()  # type: ignore

    # ==================================================
    # Execution
    # ==================================================

    def execute_batch(
        self,
        tool_calls: List[ToolCall],
        context: AgentExecutionContext,
        fail_fast: bool = True,
        retries: int = 0,
    ) -> List[ToolResult]:
        """
        Execute a batch of tool calls.

        fail_fast:
        - True  -> stop on first failure
        - False -> continue execution

        retries:
        - number of retry attempts per tool
        """
        self._init_context_state(context)

        results: List[ToolResult] = []

        for call in tool_calls:
            result = self._execute_single(call, context=context, retries=retries)
            results.append(result)
            context.tool_results.append(result)

            if fail_fast and not result.success:
                break

        return results

    def _execute_single(
        self,
        call: ToolCall,
        context: AgentExecutionContext,
        retries: int,
    ) -> ToolResult:
        """
        Execute a single tool call with retry support and observability.
        """
        # Ensure correlation id
        if not call.call_id:
            call.call_id = f"{call.tool_id}-{time.time()}"

        # Prevent duplicate execution inside one run
        if call.call_id in context.executed_tool_call_ids:
            return ToolResult(
                tool_id=call.tool_id,
                success=False,
                error=f"ToolCall '{call.call_id}' already executed",
                metadata={"duplicate": True},
            )

        started_at = datetime.now(timezone.utc)
        start_ts = time.time()

        if not self._tool_registry.has_tool(call.tool_id):
            return ToolResult(
                tool_id=call.tool_id,
                success=False,
                error="Tool not registered",
                metadata={
                    "tool_call_id": call.call_id,
                    "run_id": context.run_id,
                },
            )

        if call.tool_id not in self._executors:
            return ToolResult(
                tool_id=call.tool_id,
                success=False,
                error="No executor bound for tool",
                metadata={
                    "tool_call_id": call.call_id,
                    "run_id": context.run_id,
                },
            )

        handler = self._executors[call.tool_id]
        last_error: str | None = None

        for attempt in range(retries + 1):
            try:
                output = handler(**call.arguments)
                latency = time.time() - start_ts
                finished_at = datetime.now(timezone.utc)

                result = ToolResult(
                    tool_id=call.tool_id,
                    success=True,
                    output=output,
                    metadata={
                        "tool_call_id": call.call_id,
                        "run_id": context.run_id,
                        "attempt": attempt + 1,
                        "latency": latency,
                        "started_at": started_at.isoformat(),
                        "finished_at": finished_at.isoformat(),
                        "status": "success",
                    },
                )

                context.executed_tool_call_ids.add(call.call_id)
                return result

            except Exception as e:  # noqa: BLE001
                last_error = str(e)

        latency = time.time() - start_ts
        finished_at = datetime.now(timezone.utc)

        result = ToolResult(
            tool_id=call.tool_id,
            success=False,
            error=last_error,
            metadata={
                "tool_call_id": call.call_id,
                "run_id": context.run_id,
                "attempt": retries + 1,
                "latency": latency,
                "started_at": started_at.isoformat(),
                "finished_at": finished_at.isoformat(),
                "status": "error",
            },
        )

        context.executed_tool_call_ids.add(call.call_id)
        return result
