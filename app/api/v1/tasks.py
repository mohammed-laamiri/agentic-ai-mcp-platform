# app/api/v1/tasks.py

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from typing import List

from app.services.task_service import TaskService
from app.schemas.task import TaskCreate, TaskRead
from app.core.db import get_session

router = APIRouter()

# Dependency injection
def get_task_service(session: Session = Depends(get_session)) -> TaskService:
    return TaskService(session=session)


# -------------------------------
# Create Task
# -------------------------------
@router.post("/", response_model=TaskRead)
def create_task(task_in: TaskCreate, service: TaskService = Depends(get_task_service)):
    return service.create_task(task_in)


# -------------------------------
# Get Task by ID
# -------------------------------
@router.get("/{task_id}", response_model=TaskRead)
def get_task(task_id: str, service: TaskService = Depends(get_task_service)):
    task = service.get_task(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# -------------------------------
# List Tasks
# -------------------------------
@router.get("/", response_model=List[TaskRead])
def list_tasks(
    skip: int = 0,
    limit: int = 100,
    service: TaskService = Depends(get_task_service),
):
    return service.list_tasks(skip=skip, limit=limit)


# -------------------------------
# Complete Task
# -------------------------------
@router.post("/{task_id}/complete", response_model=TaskRead)
def complete_task(
    task_id: str,
    result: str,
    service: TaskService = Depends(get_task_service),
):
    task = service.complete_task(task_id, result)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# -------------------------------
# Fail Task
# -------------------------------
@router.post("/{task_id}/fail", response_model=TaskRead)
def fail_task(
    task_id: str,
    error: str,
    service: TaskService = Depends(get_task_service),
):
    task = service.fail_task(task_id, error)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task
