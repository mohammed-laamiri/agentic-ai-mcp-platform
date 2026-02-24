"""
Execution Router

Exposes orchestrator execution via API.
Supports SINGLE_AGENT and MULTI_AGENT automatically via planner.
"""

from fastapi import APIRouter, HTTPException, Depends

from app.schemas.task import TaskCreate
from app.schemas.execution import ExecutionResult
from app.schemas.agent import AgentRead

from app.services.orchestrator import OrchestratorService
from app.services.agent_service import AgentService
from app.services.task_service import TaskService
from app.services.planner_agent import PlannerAgent


router = APIRouter(prefix="/execution", tags=["execution"])


# ==================================================
# Dependency builder (SAFE manual wiring)
# ==================================================

def get_orchestrator() -> OrchestratorService:
    task_service = TaskService()
    agent_service = AgentService()
    planner_agent = PlannerAgent()

    return OrchestratorService(
        task_service=task_service,
        agent_service=agent_service,
        planner_agent=planner_agent,
    )


# ==================================================
# Execute endpoint
# ==================================================

@router.post("/run", response_model=ExecutionResult)
def execute_task(
    task: TaskCreate,
    orchestrator: OrchestratorService = Depends(get_orchestrator),
):
    """
    Execute task using planner + orchestrator.

    Planner decides:
    - SINGLE_AGENT
    - MULTI_AGENT
    """

    try:
        # Temporary demo agent (replace later with DB lookup)
        agent = AgentRead(
            id=1,
            name="default-agent",
            description="Default execution agent",
        )

        result = orchestrator.execute(
            agent=agent,
            task_in=task,
        )

        return result

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Execution failed: {str(exc)}",
        )