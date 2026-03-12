"""
Planner agent.

Responsible for deciding *how* a task should be executed and
assigning tools to agents (hook only, actual execution deferred).

This module implements:
- SINGLE_AGENT for simple tasks
- MULTI_AGENT (sequential) for complex tasks
- Tool assignment hooks for future integration

Async-ready for future LLM-based planning.
"""

from typing import List, Optional

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
from app.schemas.execution_plan import ExecutionPlan
from app.schemas.execution_strategy import ExecutionStrategy
from app.schemas.agent_execution_context import AgentExecutionContext
from app.schemas.tool_call import ToolCall
from app.services.rag.rag_service import RAGService


class PlannerAgent:
    """
    Decides execution strategy and assigns tools.

    Architectural role:
    - Chooses execution strategy
    - Defines agent order
    - Declares tool calls (hooks only, no execution here)

    Supports both sync and async interfaces for backward compatibility.
    """

    def __init__(self, rag_service: Optional[RAGService] = None) -> None:
        self._rag_service = rag_service

    async def plan(
        self,
        agent: AgentRead,
        task: TaskCreate,
        context: AgentExecutionContext | None = None,
    ) -> ExecutionPlan:
        """
        Produce an execution plan (async).

        Current rules:
        - Default: SINGLE_AGENT
        - Complex tasks: MULTI_AGENT (sequential)

        Future: LLM-based planning with RAG context.
        """
        # Placeholder for future async LLM call
        return self._create_plan(agent, task, context)

    def plan_sync(
        self,
        agent: AgentRead,
        task: TaskCreate,
        context: AgentExecutionContext | None = None,
    ) -> ExecutionPlan:
        """
        Synchronous version for backward compatibility.
        """
        return self._create_plan(agent, task, context)

    def _create_plan(
        self,
        agent: AgentRead,
        task: TaskCreate,
        context: AgentExecutionContext | None = None,
    ) -> ExecutionPlan:
        """
        Internal plan creation logic.
        """
        task_text = (task.description or "").lower()
        is_complex = any(
            keyword in task_text
            for keyword in [
                "analyze",
                "research",
                "compare",
                "summarize",
                "find",
                "search",
                "explain",
            ]
        )

        if is_complex:
            # Multi-agent sequential plan
            steps = self._assign_agents(task, lead_agent=agent)
            return ExecutionPlan(
                strategy=ExecutionStrategy.MULTI_AGENT,
                steps=steps,
                reason="Task classified as complex; using sequential multi-agent execution",
            )

        # Single-agent plan
        return ExecutionPlan(
            strategy=ExecutionStrategy.SINGLE_AGENT,
            reason="Task classified as simple; using single-agent execution",
        )

    # ------------------------------------------
    # Tool assignment hooks (for future use)
    # ------------------------------------------
    def _assign_agents(self, task: TaskCreate, lead_agent: AgentRead) -> List[AgentRead]:
        """
        Assigns a sequence of agents to execute this task.

        Current behavior:
        - Placeholder: uses the lead_agent twice
        - Later: assign specialized agents, tool calls, or LLM-based agents
        """
        return [lead_agent, lead_agent]

    def _assign_tools(self, task: TaskCreate, agent: AgentRead) -> List[ToolCall]:
        """
        Hook to assign tools to an agent.

        Returns a list of ToolCall objects.

        IMPORTANT:
        - This does NOT execute tools
        - Execution is handled later by the ToolExecutor
        """
        # Placeholder: no tools assigned yet
        return []
