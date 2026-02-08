# app/api/deps.py

from functools import lru_cache

from app.core.config import get_settings, Settings
from app.services.task_service import TaskService
from app.services.agent_service import AgentService
from app.services.planner_agent import PlannerAgent
from app.services.tool_registry import ToolRegistry
from app.services.memory_writer import MemoryWriter
from app.services.orchestrator import OrchestratorService
from app.services.tool_execution_engine import ToolExecutionEngine

# ==================================================
# Application settings dependency
# ==================================================
@lru_cache
def get_app_settings() -> Settings:
    """
    Returns the singleton application settings.
    """
    return get_settings()

# ==================================================
# Singleton / cached service instances
# ==================================================

@lru_cache
def get_task_service() -> TaskService:
    return TaskService()


@lru_cache
def get_agent_service() -> AgentService:
    return AgentService()


@lru_cache
def get_planner_agent() -> PlannerAgent:
    return PlannerAgent()


@lru_cache
def get_tool_registry() -> ToolRegistry:
    return ToolRegistry()


@lru_cache
def get_memory_writer() -> MemoryWriter:
    return MemoryWriter()


@lru_cache
def get_tool_execution_engine() -> ToolExecutionEngine:
    return ToolExecutionEngine(tool_registry=get_tool_registry())


@lru_cache
def get_orchestrator() -> OrchestratorService:
    """
    Returns a fully wired OrchestratorService instance.
    """
    return OrchestratorService(
        task_service=get_task_service(),
        agent_service=get_agent_service(),
        tool_registry=get_tool_registry(),
        memory_writer=get_memory_writer(),
        planner_agent=get_planner_agent(),
    )
