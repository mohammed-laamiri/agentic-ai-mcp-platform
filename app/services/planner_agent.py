"""
Planner agent.

Responsible for deciding *how* a task should be executed.

This module currently implements a very small planning logic:
- Always returns SINGLE_AGENT strategy

Future:
- Multi-agent planning
- Tool chain planning
- Conditional strategies
"""

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
from app.schemas.execution_plan import ExecutionPlan
from app.schemas.execution_strategy import ExecutionStrategy
from app.schemas.agent_execution_context import AgentExecutionContext


class PlannerAgent:
    """
    Decides execution strategy for tasks.

    NOTE:
    - This is intentionally simple for now.
    - The goal is to create a stable contract between Planner and Orchestrator.
    """

    def plan(
        self,
        agent: AgentRead,
        task: TaskCreate,
        context: AgentExecutionContext | None = None,
    ) -> ExecutionPlan:
        """
        Produce an execution plan.

        Current behavior:
        - Always chooses SINGLE_AGENT strategy
        """
        return ExecutionPlan(
            strategy=ExecutionStrategy.SINGLE_AGENT,
            reason="Default strategy for now",
        )
