"""
Planner agent.

Responsible for deciding *how* a task should be executed and
assigning tools to agents (hook only, actual execution deferred).

This module implements:
- SINGLE_AGENT for simple tasks
- MULTI_AGENT (sequential) for complex tasks
- Tool assignment hooks for future integration
- Execution trace emission
"""

from typing import List

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
from app.schemas.execution_plan import ExecutionPlan
from app.schemas.execution_strategy import ExecutionStrategy
from app.schemas.agent_execution_context import AgentExecutionContext
from app.schemas.tool_call import ToolCall


class PlannerAgent:
    """
    Decides execution strategy and assigns tools.

    Architectural role:
    - Chooses execution strategy
    - Defines agent order
    - Declares tool calls (hooks only, no execution here)
    - Emits planning trace events
    """

    # ==================================================
    # Public API
    # ==================================================

    def plan(
        self,
        agent: AgentRead,
        task: TaskCreate,
        context: AgentExecutionContext | None = None,
    ) -> ExecutionPlan:
        """
        Produce an execution plan.

        Current rules:
        - Default: SINGLE_AGENT
        - Complex tasks: MULTI_AGENT (sequential)
        """

        # --------------------------------------------------
        # Trace: planning started
        # --------------------------------------------------

        if context is not None:
            context.add_trace(
                event_type="planning_started",
                payload={
                    "agent_id": agent.id,
                    "agent_name": agent.name,
                    "task_description": task.description,
                },
            )

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

        # --------------------------------------------------
        # MULTI_AGENT plan
        # --------------------------------------------------

        if is_complex:

            steps = self._assign_agents(task, lead_agent=agent)

            plan = ExecutionPlan(
                strategy=ExecutionStrategy.MULTI_AGENT,
                steps=steps,
                reason="Task classified as complex; using sequential multi-agent execution",
            )

            if context is not None:
                context.add_trace(
                    event_type="planning_completed",
                    payload={
                        "strategy": ExecutionStrategy.MULTI_AGENT.value,
                        "agent_count": len(steps),
                        "reason": plan.reason,
                    },
                )

            return plan

        # --------------------------------------------------
        # SINGLE_AGENT plan
        # --------------------------------------------------

        plan = ExecutionPlan(
            strategy=ExecutionStrategy.SINGLE_AGENT,
            reason="Task classified as simple; using single-agent execution",
        )

        if context is not None:
            context.add_trace(
                event_type="planning_completed",
                payload={
                    "strategy": ExecutionStrategy.SINGLE_AGENT.value,
                    "agent_count": 1,
                    "reason": plan.reason,
                },
            )

        return plan

    # ==================================================
    # Agent assignment
    # ==================================================

    def _assign_agents(
        self,
        task: TaskCreate,
        lead_agent: AgentRead,
    ) -> List[AgentRead]:
        """
        Assigns a sequence of agents to execute this task.

        Current behavior:
        - Placeholder: uses lead_agent twice
        - Later: assign specialized agents
        """

        return [lead_agent, lead_agent]

    # ==================================================
    # Tool assignment hook (future)
    # ==================================================

    def _assign_tools(
        self,
        task: TaskCreate,
        agent: AgentRead,
    ) -> List[ToolCall]:
        """
        Hook to assign tools to an agent.

        IMPORTANT:
        - This does NOT execute tools
        - Execution is handled later by ToolExecutor
        """

        return []
