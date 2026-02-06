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
from typing import Callable, Dict, List

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
        results: List[ToolResult] = []

        for call in tool_calls:
            result = self._execute_single(call, retries=retries)
            results.append(result)
            context.tool_results.append(result)

            if fail_fast and not result.success:
                break

        return results

    def _execute_single(self, call: ToolCall, retries: int) -> ToolResult:
        """
        Execute a single tool call with retry support.
        """
        start = time.time()

        if not self._tool_registry.has_tool(call.tool_id):
            return ToolResult(
                tool_id=call.tool_id,
                success=False,
                error="Tool not registered",
                metadata={},
            )

        if call.tool_id not in self._executors:
            return ToolResult(
                tool_id=call.tool_id,
                success=False,
                error="No executor bound for tool",
                metadata={},
            )

        handler = self._executors[call.tool_id]

        last_error: str | None = None

        for attempt in range(retries + 1):
            try:
                output = handler(**call.arguments)
                latency = time.time() - start

                return ToolResult(
                    tool_id=call.tool_id,
                    success=True,
                    output=output,
                    metadata={
                        "latency": latency,
                        "attempt": attempt + 1,
                    },
                )

            except Exception as e:
                last_error = str(e)

        latency = time.time() - start

        return ToolResult(
            tool_id=call.tool_id,
            success=False,
            error=last_error,
            metadata={
                "latency": latency,
                "attempt": retries + 1,
            },
        )
