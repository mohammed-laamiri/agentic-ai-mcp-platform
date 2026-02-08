# app/api/routers/agent_router.py

from fastapi import APIRouter, Depends, HTTPException

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate
from app.schemas.execution import ExecutionResult
from app.services.orchestrator import OrchestratorService
from app.api.deps import get_orchestrator

router = APIRouter(prefix="/agent", tags=["Agent"])


@router.post("/execute", response_model=ExecutionResult)
def execute_agent(
    task_in: TaskCreate,
    agent: AgentRead,
    orchestrator: OrchestratorService = Depends(get_orchestrator),
) -> ExecutionResult:
    """
    Execute a task using an agent and return structured ExecutionResult.

    Notes:
    - Does NOT persist the task in the task store.
    - Designed for direct agent execution / testing.
    - Tool calls (if any) are executed according to MCP ToolExecutionEngine.
    """
    try:
        return orchestrator.execute(agent=agent, task_in=task_in)
    except Exception as exc:
        # Return clean HTTP 500 response for unhandled errors
        raise HTTPException(status_code=500, detail=str(exc))


@router.get("/health", status_code=200)
def agent_health() -> dict:
    """
    Health check endpoint for the agent router.
    """
    return {"status": "ok", "router": "agent"}
