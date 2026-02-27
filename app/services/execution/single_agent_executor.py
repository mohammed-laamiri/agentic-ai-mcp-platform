"""
SingleAgentExecutor

Responsible for executing ONE agent.
Does NOT orchestrate multiple agents.
Does NOT create plans.

This is the lowest-level execution unit.
"""

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
from app.schemas.execution import ExecutionResult
from app.schemas.agent_execution_context import AgentExecutionContext

from app.services.agent_service import AgentService


class SingleAgentExecutor:
    """
    Executes a single agent.

    Responsibilities:
    - Receive agent
    - Execute agent logic
    - Return result

    Does NOT:
    - Know about plans
    - Know about orchestration
    """

    def __init__(self, agent_service: AgentService) -> None:
        self._agent_service = agent_service

    # ==================================================
    # Public API
    # ==================================================

    def execute(
        self,
        agent: AgentRead,
        task_in: TaskCreate,
        context: AgentExecutionContext,
    ) -> ExecutionResult:
        """
        Execute ONE agent.

        Input:
        - agent: Agent to execute
        - task_in: TaskCreate object
        - context: shared execution context

        Returns:
        - ExecutionResult
        """

        # --------------------------------------------------
        # Execute agent using AgentService
        # --------------------------------------------------
        raw_result = self._agent_service.execute(
            agent=agent,
            task=task_in,
            context=context,
        )

        # --------------------------------------------------
        # Collect any declared tool calls in context
        # --------------------------------------------------
        tool_calls = raw_result.get("tool_calls", [])
        for call in tool_calls:
            if isinstance(call, dict):
                from app.schemas.tool_call import ToolCall
                context.add_tool_call(ToolCall(**call))
            elif hasattr(call, "__class__") and call.__class__.__name__ == "ToolCall":
                context.add_tool_call(call)

        # --------------------------------------------------
        # Return ExecutionResult
        # --------------------------------------------------
        if isinstance(raw_result, ExecutionResult):
            return raw_result

        if isinstance(raw_result, dict):
            return ExecutionResult(**raw_result)

        raise TypeError(
            f"AgentService returned invalid result type: {type(raw_result)}"
        )