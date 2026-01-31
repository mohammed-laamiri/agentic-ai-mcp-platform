"""
Base tool contract.

All tools MUST implement this interface.
"""

from typing import Protocol
from app.schemas.tool_execution import ToolExecutionResult
from app.schemas.agent_execution_context import AgentExecutionContext


class Tool(Protocol):
    tool_id: str
    name: str
    version: str

    def execute(
        self,
        input: dict,
        context: AgentExecutionContext | None = None,
    ) -> ToolExecutionResult:
        ...
