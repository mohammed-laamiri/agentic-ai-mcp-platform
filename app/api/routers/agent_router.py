# app/api/routers/agent_router.py

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.task import TaskRead, TaskCreate
from app.services.task_service import TaskService

router = APIRouter(tags=["Agents"])

# ----------------------------
# Use the same singleton TaskService
# ----------------------------
task_service = TaskService()

def get_task_service() -> TaskService:
    return task_service

# ----------------------------
# Agent Endpoints
# ----------------------------

@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_agent_task(task_in: TaskCreate, service: TaskService = Depends(get_task_service)):
    return service.create_task(task_in)


@router.get("/{task_id}", response_model=TaskRead)
def get_agent_task(task_id: str, service: TaskService = Depends(get_task_service)):
    task = service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.get("/", response_model=List[TaskRead])
def list_agent_tasks(skip: int = 0, limit: int = 100, service: TaskService = Depends(get_task_service)):
    return service.list_tasks(skip=skip, limit=limit)


@router.post("/{task_id}/complete", response_model=TaskRead)
def complete_agent_task(
    task_id: str,
    result: Optional[Dict[str, Any]] = None,
    service: TaskService = Depends(get_task_service)
):
    task = service.complete_task(task_id, result or {})
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.post("/{task_id}/fail", response_model=TaskRead)
def fail_agent_task(task_id: str, error: str, service: TaskService = Depends(get_task_service)):
    task = service.fail_task(task_id, error)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task
