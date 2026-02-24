"""
Multi-Agent Execution Service (v1)

Handles execution across multiple agents while preserving execution context.

This module does NOT replace OrchestratorService.
It provides reusable execution strategies that the orchestrator can call.

Supports:
- Sequential execution (current)
- Parallel execution (future)
"""

from typing import List, Optional

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
from app.schemas.execution import ExecutionResult
from app.schemas.agent_execution_context import AgentExecutionContext
from app.schemas.tool_call import ToolCall

from app.services.agent_service import AgentService


class MultiAgentExecutor:
    """
    Executes tasks across multiple agents.

    Responsibilities:
    - Execute agents sequentially
    - Maintain execution context
    - Collect tool calls
    - Return final execution result
    """

    def __init__(self, agent_service: AgentService) -> None:
        self._agent_service = agent_service

    # ==========================================================
    # Sequential execution strategy
    # ==========================================================

    def execute_sequential(
        self,
        agents: List[AgentRead],
        task_in: TaskCreate,
        context: AgentExecutionContext,
    ) -> ExecutionResult:
        """
        Executes agents sequentially.

        Output of each agent becomes input of next agent.
        """

        current_input: str = task_in.description or ""
        final_result: Optional[ExecutionResult] = None

        for agent in agents:

            intermediate_task = TaskCreate(
                description=current_input,
                input=current_input,
            )

            raw_result = self._agent_service.execute(
                agent=agent,
                task=intermediate_task,
                context=context,
            )

            self._collect_tool_calls(raw_result, context)

            final_result = ExecutionResult(**raw_result)

            # Pass output forward
            current_input = final_result.output or ""

        if final_result is None:
            raise RuntimeError("Multi-agent execution produced no result")

        return final_result

    # ==========================================================
    # Tool call collection
    # ==========================================================

    def _collect_tool_calls(
        self,
        raw_result: dict,
        context: AgentExecutionContext,
    ) -> None:
        """
        Safely collect tool calls into execution context.
        """

        tool_calls = raw_result.get("tool_calls", [])

        if not tool_calls:
            return

        for call in tool_calls:

            if isinstance(call, ToolCall):
                context.add_tool_call(call)

            elif isinstance(call, dict):
                context.add_tool_call(ToolCall(**call))