"""
Execution plan schema.

Represents the output of the planning phase.

Defines HOW execution should occur, not the result.

Acts as the contract between:
- PlannerAgent → produces ExecutionPlan
- OrchestratorService → executes ExecutionPlan
"""

from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict

from app.schemas.execution_strategy import ExecutionStrategy
from app.schemas.agent import AgentRead
from app.schemas.tool_call import ToolCall


class ExecutionPlan(BaseModel):
    """
    Execution plan produced by PlannerAgent.

    PURPOSE:
    - Separate planning from execution
    - Explicitly define execution strategy
    - Enable multi-agent workflows
    - Support tool-aware execution
    - Enable future parallel execution strategies

    IMPORTANT:
    - Orchestrator interprets this plan
    - Executor executes the steps
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    # ==================================================
    # Execution strategy
    # ==================================================

    strategy: ExecutionStrategy = Field(
        ...,
        description="Execution strategy selected by planner",
        examples=["single_agent", "multi_agent"],
    )

    # ==================================================
    # Agent execution steps
    # ==================================================

    steps: List[AgentRead] = Field(
        default_factory=list,
        description=(
            "Ordered list of agents to execute. "
            "Sequential execution is currently supported."
        ),
    )

    # ==================================================
    # Tool execution declarations (optional)
    # ==================================================

    tool_calls: List[ToolCall] = Field(
        default_factory=list,
        description=(
            "Optional tool calls declared during planning. "
            "Execution handled by orchestrator."
        ),
    )

    # ==================================================
    # Planner reasoning (optional, but valuable)
    # ==================================================

    reason: Optional[str] = Field(
        default=None,
        description="Explanation for strategy selection",
    )

    # ==================================================
    # Validation helpers
    # ==================================================

    def is_single_agent(self) -> bool:
        return self.strategy == ExecutionStrategy.SINGLE_AGENT

    def is_multi_agent(self) -> bool:
        return self.strategy == ExecutionStrategy.MULTI_AGENT

    def step_count(self) -> int:
        return len(self.steps)