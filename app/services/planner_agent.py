"""
Planner agent.

Responsible for deciding *how* a task should be executed.

This module currently implements a small but expandable planning logic:
- SINGLE_AGENT for simple tasks
- MULTI_AGENT (sequential) for complex tasks

Future:
- LLM-based planning
- Tool chain planning
- Conditional and branching strategies
"""

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
from app.schemas.execution_plan import ExecutionPlan
from app.schemas.execution_strategy import ExecutionStrategy
from app.schemas.agent_execution_context import AgentExecutionContext


class PlannerAgent:
    """
    Decides execution strategy for tasks.

    Architectural role:
    - Chooses strategy
    - Defines execution order (not execution itself)
    """

    def plan(
        self,
        agent: AgentRead,
        task: TaskCreate,
        context: AgentExecutionContext | None = None,
    ) -> ExecutionPlan:
        """
        Produce an execution plan.

        Current planning rules (intentionally simple):
        - Default: SINGLE_AGENT
        - If task appears complex: MULTI_AGENT (sequential)
        """

        # ----------------------------------
        # Naive complexity heuristic (v0)
        # ----------------------------------
        task_text = task.description.lower()

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
            return ExecutionPlan(
                strategy=ExecutionStrategy.MULTI_AGENT,
                steps=[
                    agent,  # Planner-selected lead agent (for now)
                    agent,  # Placeholder for future specialized agents
                ],
                reason="Task classified as complex; using sequential multi-agent execution",
            )

        # ----------------------------------
        # Default: SINGLE_AGENT
        # ----------------------------------
        return ExecutionPlan(
            strategy=ExecutionStrategy.SINGLE_AGENT,
            reason="Task classified as simple; using single-agent execution",
        )
