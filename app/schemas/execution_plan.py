"""
Execution plan schema.

Represents the result of the planning phase.
Defines HOW a task should be executed, not the result.

Acts as a contract between:
- PlannerAgent (produces plan)
- OrchestratorService (interprets plan)
"""

from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.execution_strategy import ExecutionStrategy
from app.schemas.agent import AgentRead
from app.schemas.tool_call import ToolCall


class ExecutionPlan(BaseModel):
    """
    Execution plan produced by the PlannerAgent.

    WHY THIS EXISTS:
    - Separates planning from execution
    - Makes execution decisions explicit
    - Enables future multi-step / multi-agent plans
    - Allows tool-aware execution without coupling runtime logic
    """

    strategy: ExecutionStrategy = Field(
        ...,
        description="Execution strategy chosen by the planner",
    )

    steps: Optional[List[AgentRead]] = Field(
        default=None,
        description=(
            "Ordered list of agents to execute sequentially. "
            "Required when strategy is MULTI_AGENT."
        ),
    )

    tool_calls: Optional[List[ToolCall]] = Field(
        default=None,
        description=(
            "Optional list of tool calls required by this execution plan. "
            "Execution order is determined by the orchestrator."
        ),
    )

    reason: Optional[str] = Field(
        default=None,
        description="Optional explanation for why this strategy was chosen",
    )
