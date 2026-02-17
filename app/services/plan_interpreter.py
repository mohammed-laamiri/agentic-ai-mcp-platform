"""
Plan Interpreter
================

Converts ExecutionPlan into executable steps.

This version is schema-agnostic and works with your existing ExecutionPlan schema.
"""

from typing import List, Any

from app.schemas.execution_plan import ExecutionPlan


class PlanInterpreter:
    """
    Converts ExecutionPlan into executable steps.

    Does NOT assume specific step class type.
    Works with your current schema safely.
    """

    def interpret(
        self,
        plan: ExecutionPlan,
    ) -> List[Any]:
        """
        Extract steps from execution plan.

        Parameters
        ----------
        plan : ExecutionPlan

        Returns
        -------
        List[Any]
            Execution steps
        """

        # Safety check
        if plan is None:
            return []

        # Ensure steps attribute exists
        if not hasattr(plan, "steps"):
            raise ValueError(
                "ExecutionPlan missing required attribute: steps"
            )

        # Ensure steps is iterable
        if plan.steps is None:
            return []

        if not isinstance(plan.steps, list):
            raise ValueError(
                "ExecutionPlan.steps must be a list"
            )

        return plan.steps
