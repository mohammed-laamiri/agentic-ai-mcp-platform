# app/api/routers/task_router.py

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.task import TaskCreate, TaskRead
from app.schemas.agent import AgentRead
from app.services.orchestrator import OrchestratorService
from app.services.task_service import TaskService
from app.api.deps import get_orchestrator, get_task_service

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/run", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def run_task(
    task_in: TaskCreate,
    agent: AgentRead,
    orchestrator: OrchestratorService = Depends(get_orchestrator),
) -> TaskRead:
    """
    Run a task using a selected agent.

    Orchestrates the full execution including:
    - Agent execution
    - Multi-agent planning
    - Tool calls (MCP)
    - Memory persistence
    - Task persistence
    """
    try:
        return orchestrator.run(agent=agent, task_in=task_in)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/", response_model=List[TaskRead])
def list_tasks(
    task_service: TaskService = Depends(get_task_service),
) -> List[TaskRead]:
    """
    List all persisted tasks.

    Uses TaskService as the source of truth.
    """
    try:
        # Ensure your TaskService has a list_tasks() method
        return task_service.list_tasks()
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/{task_id}", response_model=TaskRead)
def get_task(
    task_id: str,
    task_service: TaskService = Depends(get_task_service),
) -> TaskRead:
    """
    Retrieve a task by ID.
    """
    task = task_service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get("/health", status_code=status.HTTP_200_OK)
def tasks_health() -> dict:
    """
    Health check for the task router.
    """
    return {"status": "ok", "router": "tasks"}
