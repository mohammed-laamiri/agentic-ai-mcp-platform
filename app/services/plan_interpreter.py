"""
Plan Interpreter
================

Converts ExecutionPlan into executable agent sequence.

Aligned with ExecutionPlan schema:
    steps: Optional[List[AgentRead]]

This layer isolates orchestration logic from planner and runtime.
"""

from typing import List

from app.schemas.execution_plan import ExecutionPlan
from app.schemas.agent import AgentRead


class PlanInterpreter:
    """
    Extracts agent execution sequence from ExecutionPlan.
    """

    def interpret(
        self,
        plan: ExecutionPlan,
    ) -> List[AgentRead]:
        """
        Extract ordered list of agents to execute.

        Parameters
        ----------
        plan : ExecutionPlan

        Returns
        -------
        List[AgentRead]
            Agents to execute in order.
        """

        if plan is None:
            return []

        if plan.steps is None:
            return []

        if not isinstance(plan.steps, list):
            raise ValueError(
                "ExecutionPlan.steps must be a list of AgentRead"
            )

        return plan.steps
