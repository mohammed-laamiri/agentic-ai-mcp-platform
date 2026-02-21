"""
Task API router.

Exposes endpoints to run tasks using agents.
"""

from fastapi import APIRouter, Depends

from app.schemas.task import TaskCreate, TaskRead
from app.schemas.agent import AgentRead
from app.services.orchestrator import OrchestratorService
from app.api.deps import get_orchestrator

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/run", response_model=TaskRead)
def run_task(
    task_in: TaskCreate,
    agent: AgentRead,
    orchestrator: OrchestratorService = Depends(get_orchestrator),
) -> TaskRead:
    """
    Run a task using a selected agent.
    """
    return orchestrator.run(agent=agent, task_in=task_in)