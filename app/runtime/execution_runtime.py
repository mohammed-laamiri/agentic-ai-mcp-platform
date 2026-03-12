"""
Execution Runtime.

Per-execution runtime controller.

Responsibilities:
- Own AgentExecutionContext
- Execute tools via ToolExecutionEngine
- Track tool calls and results
"""

from typing import Optional

from app.schemas.agent_execution_context import AgentExecutionContext
from app.schemas.tool_call import ToolCall
from app.schemas.tool_result import ToolResult
from app.services.tool_execution_engine import ToolExecutionEngine


class ExecutionRuntime:
    """
    Runtime controller for a single orchestrator run.
    """

    def __init__(
        self,
        tool_execution_engine: ToolExecutionEngine,
        context: Optional[AgentExecutionContext] = None,
    ) -> None:
        self._engine = tool_execution_engine
        self._context = context or AgentExecutionContext()

    @property
    def context(self) -> AgentExecutionContext:
        return self._context

    def execute_tool(self, tool_call: ToolCall) -> ToolResult:
        """
        Execute a tool and track execution.
        """
        # Track declared tool call
        self._context.add_tool_call(tool_call)

        # Execute via engine
        result = self._engine.execute(
            tool_call=tool_call,
            context=self._context,
        )

        # Track result
        self._context.add_tool_result(result)

        return result

    def get_run_id(self) -> str:
        return self._context.run_id

    def get_tool_calls(self):
        return self._context.tool_calls

    def get_tool_results(self):
        return self._context.tool_results