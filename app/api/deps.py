"""
Dependency Injection Container.

Provides clean construction of services for FastAPI routes.

Ensures proper wiring of:
- Services
- Registries
- Repositories
- Runtime components

This avoids circular dependencies and keeps orchestration clean.
"""

from app.services.planner_agent import PlannerAgent
from app.services.task_service import TaskService
from app.services.agent_service import AgentService
from app.services.orchestrator import OrchestratorService
from app.services.tool_registry import ToolRegistry

from app.repositories.execution_history_repository import ExecutionHistoryRepository
from app.repositories.execution_trace_repository import ExecutionTraceRepository


# ============================================================
# Core Services
# ============================================================

def get_task_service() -> TaskService:
    return TaskService()


def get_agent_service() -> AgentService:
    return AgentService()


def get_planner_agent() -> PlannerAgent:
    return PlannerAgent()


# ============================================================
# Registries
# ============================================================

def get_tool_registry() -> ToolRegistry:
    return ToolRegistry()


# ============================================================
# Repositories
# ============================================================

def get_execution_history_repository() -> ExecutionHistoryRepository:
    return ExecutionHistoryRepository()


def get_execution_trace_repository() -> ExecutionTraceRepository:
    return ExecutionTraceRepository()


# ============================================================
# Orchestrator
# ============================================================

def get_orchestrator() -> OrchestratorService:
    """
    Fully wired orchestrator with repositories and registries.

    Note: Only passes supported constructor arguments.
    Additional repositories or writers can be injected via
    method calls or context after instantiation.
    """

    return OrchestratorService(
        task_service=get_task_service(),
        agent_service=get_agent_service(),
        planner_agent=get_planner_agent(),
    )
