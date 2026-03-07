# app/api/routers/task_router.py

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.task import TaskCreate, TaskRead
from app.schemas.agent import AgentRead
from app.services.task_service import TaskService
from app.services.agent_service import AgentService
from app.services.tool_registry import ToolRegistry
from app.services.memory_writer import MemoryWriter
from app.services.orchestrator import OrchestratorService

router = APIRouter(tags=["Tasks"])

# ----------------------------
# Singleton TaskService (shared in-memory store)
# ----------------------------
task_service = TaskService()

def get_task_service() -> TaskService:
    return task_service


def get_orchestrator() -> OrchestratorService:
    """Create orchestrator with in-memory services."""
    return OrchestratorService(
        task_service=task_service,
        agent_service=AgentService(),
        tool_registry=ToolRegistry(),
        memory_writer=MemoryWriter(),
    )

# ----------------------------
# CRUD Endpoints
# ----------------------------

@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(task_in: TaskCreate, service: TaskService = Depends(get_task_service)):
    return service.create_task(task_in)


@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: str, service: TaskService = Depends(get_task_service)):
    task = service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.get("/", response_model=List[TaskRead])
def list_tasks(skip: int = 0, limit: int = 100, service: TaskService = Depends(get_task_service)):
    return service.list_tasks(skip=skip, limit=limit)


@router.post("/{task_id}/complete", response_model=TaskRead)
def complete_task(
    task_id: str,
    result: Optional[Dict[str, Any]] = None,
    service: TaskService = Depends(get_task_service)
):
    task = service.complete_task(task_id, result or {})
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.post("/{task_id}/fail", response_model=TaskRead)
def fail_task(task_id: str, error: str, service: TaskService = Depends(get_task_service)):
    task = service.fail_task(task_id, error)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.post("/{task_id}/execute", response_model=TaskRead)
def execute_task(
    task_id: str,
    service: TaskService = Depends(get_task_service),
    orchestrator: OrchestratorService = Depends(get_orchestrator),
):
    """
    Execute a task via the orchestrator.

    Creates a default agent and runs the task through the orchestration pipeline.
    """
    task = service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    # Create a default agent for execution
    default_agent = AgentRead(id="default-agent", name="DefaultAgent")

    # Create TaskCreate from existing task
    task_create = TaskCreate(
        name=task.name,
        description=task.description,
        input=task.input,
        priority=task.priority,
    )

    # Execute via orchestrator (this creates a new task and completes it)
    # We need to update the original task instead
    result = orchestrator.execute(agent=default_agent, task_in=task_create)

    # Complete the original task with the execution result
    completed_task = service.complete_task(
        task_id=task_id,
        result=result.model_dump() if hasattr(result, 'model_dump') else result.dict(),
    )

    return completed_task
