"""
Execution Router

- Exposes orchestrator execution via API.
- Supports SINGLE_AGENT and MULTI_AGENT via planner.
- Phase 4 applied:
    - Auth (API key) at route boundary
    - Rate limiting per IP
    - Correlation IDs available in logs
"""

from fastapi import APIRouter, HTTPException, Depends
from slowapi import Limiter

from app.schemas.task import TaskCreate
from app.schemas.execution import ExecutionResult
from app.schemas.agent import AgentRead

from app.services.orchestrator import OrchestratorService
from app.services.agent_service import AgentService
from app.services.task_service import TaskService
from app.services.planner_agent import PlannerAgent
from app.services.execution.execution_service import ExecutionService

# Phase 4.1 — Auth dependency
from app.api.dependencies.auth import require_api_key

# Phase 4.3 — Rate limiting
from app.api.rate_limit import limiter

router = APIRouter(prefix="/execution", tags=["execution"])


# ==================================================
# Dependency builder (Safe manual wiring)
# ==================================================
def get_orchestrator() -> OrchestratorService:
    """
    Constructs orchestrator with all required services.
    Phase 4 safe: adds execution_service required by constructor.
    """
    task_service = TaskService()
    agent_service = AgentService()
    planner_agent = PlannerAgent()
    execution_service = ExecutionService()

    return OrchestratorService(
        task_service=task_service,
        agent_service=agent_service,
        planner_agent=planner_agent,
        execution_service=execution_service,  # Required argument
    )


# ==================================================
# Execute endpoint (with auth + rate limiting)
# ==================================================
@router.post("/run", response_model=ExecutionResult)
@limiter.limit("10/minute")  # Phase 4.3: 10 requests per minute per IP
def execute_task(
    task: TaskCreate,
    orchestrator: OrchestratorService = Depends(get_orchestrator),
    _: str = Depends(require_api_key),  # Phase 4.1: API key enforcement
):
    """
    Executes a task using the orchestrator + planner.

    Planner decides:
    - SINGLE_AGENT
    - MULTI_AGENT

    Notes:
    - Auth applied at API boundary
    - Rate limiting applied
    - Correlation IDs automatically available in logs
    - Domain layer untouched
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
        # Capture and return clean 500
        raise HTTPException(
            status_code=500,
            detail=f"Execution failed: {str(exc)}",
        )