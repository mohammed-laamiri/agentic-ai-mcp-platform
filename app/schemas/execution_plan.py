"""
Execution Plan schema.

Represents the output of the planning phase.

Architectural intent:
- This model describes WHAT should happen, not HOW
- It is produced by a Planner Agent
- It is consumed by the Orchestrator

Current responsibilities:
- Describe a single-step execution plan

Future responsibilities (by design):
- Multi-step plans
- Agent routing
- Tool invocation graphs
- LangGraph-compatible DAGs
"""

from pydantic import BaseModel, Field


class ExecutionPlan(BaseModel):
    """
    Planner output describing the intended execution strategy.

    IMPORTANT:
    - This is NOT an execution result
    - This does NOT contain business output
    """

    strategy: str = Field(
        default="single_agent",
        description="Execution strategy identifier",
    )

    reasoning: str = Field(
        default="Default single-agent execution",
        description="Planner reasoning (human-readable, optional)",
    )
