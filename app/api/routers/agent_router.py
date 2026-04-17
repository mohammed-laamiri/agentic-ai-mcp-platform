"""
Agent API router.

Exposes endpoints for:
- Agent task CRUD operations (separate storage from task_router)
- Direct agent execution
"""

from typing import List, Optional, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate, TaskRead
from app.schemas.execution import ExecutionResult
from app.services.task_service import TaskService
from app.services.orchestrator import OrchestratorService
from app.api.deps import get_orchestrator

router = APIRouter(prefix="/agents", tags=["Agent"])


# ---------------------------------------------------------
# Singleton TaskService (separate from task_router)
# ---------------------------------------------------------

task_service = TaskService()


def get_task_service() -> TaskService:
    return task_service


# ---------------------------------------------------------
# CRUD Endpoints for Agent Tasks
# ---------------------------------------------------------

@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_agent_task(
    task_in: TaskCreate,
    service: TaskService = Depends(get_task_service),
):
    """Create a new task via the agent endpoint."""
    return service.create_task(task_in)


@router.get("/", response_model=List[TaskRead])
def list_agent_tasks(
    skip: int = 0,
    limit: int = 100,
    service: TaskService = Depends(get_task_service),
):
    """List all tasks created via the agent endpoint."""
    return service.list_tasks(skip=skip, limit=limit)


@router.get("/{task_id}", response_model=TaskRead)
def get_agent_task(
    task_id: str,
    service: TaskService = Depends(get_task_service),
):
    """Get an agent task by ID."""
    task = service.get_task(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return task


@router.post("/{task_id}/complete", response_model=TaskRead)
def complete_agent_task(
    task_id: str,
    result: Optional[Dict[str, Any]] = None,
    service: TaskService = Depends(get_task_service),
):
    """Mark an agent task as completed."""
    task = service.complete_task(task_id, result or {})
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return task


@router.post("/{task_id}/fail", response_model=TaskRead)
def fail_agent_task(
    task_id: str,
    error: str,
    service: TaskService = Depends(get_task_service),
):
    """Mark an agent task as failed."""
    task = service.fail_task(task_id, error)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )
    return task


# ---------------------------------------------------------
# Direct Execution Endpoint
# ---------------------------------------------------------

@router.post("/execute", response_model=ExecutionResult)
def execute_agent(
    task_in: TaskCreate,
    agent: AgentRead,
    orchestrator: OrchestratorService = Depends(get_orchestrator),
) -> ExecutionResult:
    """
    Execute a task using an agent and return structured ExecutionResult.

    Note:
    - This endpoint does NOT persist the task.
    - Intended for direct agent execution calls.
    """
    return orchestrator.execute_sync(agent=agent, task_in=task_in)
