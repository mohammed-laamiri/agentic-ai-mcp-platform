from fastapi import APIRouter, Depends
from typing import List

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
    # Minimal placeholder logic
    return orchestrator.run(agent=agent, task_in=task_in)


@router.get("/", response_model=List[TaskRead])
def list_tasks(
    orchestrator: OrchestratorService = Depends(get_orchestrator),
) -> List[TaskRead]:
    """
    List all tasks.
    """
    # Minimal placeholder logic
    return orchestrator.list_tasks()