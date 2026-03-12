# app/api/routers/demo_router.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Any, List

from app.services.orchestrator import OrchestratorService
from app.services.agent_service import AgentService
from app.services.task_service import TaskService
from app.services.planner_agent import PlannerAgent

router = APIRouter()

# -----------------------------
# Request & Response Schemas
# -----------------------------
class DemoRequest(BaseModel):
    message: str

class ToolCallResponse(BaseModel):
    tool_call_id: str | None
    tool_id: str
    success: bool
    output: Any
    error: str | None
    started_at: str
    finished_at: str

class DemoResponse(BaseModel):
    tool_results: List[ToolCallResponse]

# -----------------------------
# Dependency injection
# -----------------------------
def get_orchestrator() -> OrchestratorService:
    task_service = TaskService()
    agent_service = AgentService()
    planner_agent = PlannerAgent()
    return OrchestratorService(task_service, agent_service, planner_agent)

# -----------------------------
# Multi-Agent Demo Endpoint
# -----------------------------
@router.post("/demo/multi-agent", response_model=DemoResponse)
def multi_agent_demo(payload: DemoRequest, orchestrator: OrchestratorService = Depends(get_orchestrator)):
    """
    Multi-agent demo:
    - The task flows through multiple agents sequentially.
    - Each agent produces tool calls which are collected in execution context.
    """

    from app.schemas.agent import AgentRead
    from app.schemas.task import TaskCreate

    # Define two or more dummy agents
    agents = [
        AgentRead(agent_id="agent_1", name="Agent One"),
        AgentRead(agent_id="agent_2", name="Agent Two"),
    ]

    # Initial task
    demo_task = TaskCreate(description=payload.message, input=payload.message)

    all_tool_results: List[ToolCallResponse] = []
    current_task = demo_task

    try:
        for agent in agents:
            # Execute task for the agent
            execution_result = orchestrator.execute(agent, current_task)

            # Collect tool results
            for tc in execution_result.tool_results:
                all_tool_results.append(
                    ToolCallResponse(
                        tool_call_id=tc.tool_call_id,
                        tool_id=tc.tool_id,
                        success=tc.success,
                        output=tc.output,
                        error=tc.error,
                        started_at=tc.started_at.isoformat(),
                        finished_at=tc.finished_at.isoformat(),
                    )
                )

            # Pass the output to the next agent
            current_task = TaskCreate(
                description=execution_result.output or "",
                input=execution_result.output or ""
            )

        return DemoResponse(tool_results=all_tool_results)

    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Multi-agent demo failed: {str(exc)}")