from fastapi import APIRouter, Depends
from typing import List

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

    Minimal placeholder logic for MVP.
    """
    return orchestrator.execute(agent=agent, task_in=task_in)


@router.get("/", response_model=List[AgentRead])
def list_agents(
    orchestrator: OrchestratorService = Depends(get_orchestrator),
) -> List[AgentRead]:
    """
    List all available agents.
    """
    return orchestrator.list_agents()