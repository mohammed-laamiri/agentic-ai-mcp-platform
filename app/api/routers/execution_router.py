"""
Execution Router (Async-Safe, Phase 4)

- Exposes orchestrator execution via API.
- Supports SINGLE_AGENT and MULTI_AGENT via planner.
- Auth (API key) at route boundary
- Rate limiting per IP
- Correlation IDs available in logs
- Async compatible with updated OrchestratorService
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.responses import StreamingResponse
from slowapi import Limiter
import json
import asyncio

from app.schemas.task import TaskCreate
from app.schemas.execution import ExecutionResult
from app.schemas.agent import AgentRead

from app.services.orchestrator import OrchestratorService
from app.services.agent_service import AgentService
from app.services.task_service import TaskService
from app.services.planner_agent import PlannerAgent
from app.services.execution.execution_service import ExecutionService

from app.api.dependencies.auth import require_api_key
from app.api.rate_limit import limiter

router = APIRouter(prefix="/execution", tags=["execution"])


# ==================================================
# Dependency builder
# ==================================================
def get_orchestrator() -> OrchestratorService:
    task_service = TaskService()
    agent_service = AgentService()
    planner_agent = PlannerAgent()
    execution_service = ExecutionService()

    return OrchestratorService(
        task_service=task_service,
        agent_service=agent_service,
        planner_agent=planner_agent,
        execution_service=execution_service,
    )


# ==================================================
# Execute endpoint (non-streaming, async)
# ==================================================
@router.post("/run", response_model=ExecutionResult)
@limiter.limit("10/minute")
async def execute_task(
    request: Request,
    task: TaskCreate,
    orchestrator: OrchestratorService = Depends(get_orchestrator),
    _: str = Depends(require_api_key),
):
    try:
        agent = AgentRead(
            id=1,
            name="default-agent",
            description="Default execution agent",
        )
        result: ExecutionResult = await orchestrator.execute(
            agent=agent,
            task_in=task,
        )
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Execution failed: {str(exc)}")


# ==================================================
# Streaming execution endpoint (SSE)
# ==================================================
@router.post("/stream")
@limiter.limit("5/minute")  # fewer per IP for streaming
async def stream_execute_task(
    request: Request,
    task: TaskCreate,
    orchestrator: OrchestratorService = Depends(get_orchestrator),
    _: str = Depends(require_api_key),
):
    """
    Stream execution events as Server-Sent Events (SSE).
    """
    agent = AgentRead(
        id=1,
        name="default-agent",
        description="Default execution agent",
    )

    async def event_generator():
        try:
            async for event in orchestrator.stream_execute(agent=agent, task_in=task):
                yield f"data: {json.dumps(event.model_dump())}\n\n"
        except Exception as exc:
            yield f"data: {json.dumps({'type': 'ERROR', 'detail': str(exc)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
    )