"""
Planner Agent.

This module is responsible for deciding HOW a task should be executed.

Architectural intent:
- Encapsulates planning logic
- Produces a typed ExecutionPlan
- Does NOT execute tasks
- Does NOT persist data

Current behavior:
- Deterministic stub
- Always returns a single-step execution plan

Future behavior (by design):
- Multi-agent routing
- Tool selection
- LangGraph DAG generation
- MCP-compatible execution graphs
"""

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
from app.schemas.execution_plan import ExecutionPlan
from app.schemas.agent_execution_context import AgentExecutionContext


class PlannerAgent:
    """
    Planner Agent.

    Responsible for translating intent into an execution plan.
    """

    def plan(
        self,
        agent: AgentRead,
        task: TaskCreate,
        context: AgentExecutionContext,
    ) -> ExecutionPlan:
        """
        Produce an execution plan.

        Why this exists:
        - Separates planning from execution
        - Makes orchestration explicit
        - Prevents Orchestrator from becoming "smart"

        Current behavior:
        - Always returns a single-agent execution plan
        - Context is accepted but not used (by design)
        """
        return ExecutionPlan()
