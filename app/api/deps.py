# app/api/deps.py

"""
Dependency injection module for FastAPI.

Responsibilities:
- Provide application-wide singleton services
- Wire database session to services
- Support dependency injection for routers and endpoints
- Keep services decoupled from API endpoints
"""

from functools import lru_cache
from fastapi import Depends
from sqlmodel import Session

from app.core.config import get_settings, Settings
from app.core.db import get_session
from app.services.task_service import TaskService
from app.services.agent_service import AgentService
from app.services.planner_agent import PlannerAgent
from app.services.tool_registry import ToolRegistry
from app.services.memory_writer import MemoryWriter
from app.services.orchestrator import OrchestratorService
from app.services.tool_execution_engine import ToolExecutionEngine


# ==================================================
# Database session dependency
# ==================================================
def get_db_session(session: Session = Depends(get_session)) -> Session:
    """
    Provides a SQLModel Session per request.

    Usage:
        db: Session = Depends(get_db_session)
    """
    return session


# ==================================================
# Application settings dependency
# ==================================================
@lru_cache
def get_app_settings() -> Settings:
    """
    Returns the singleton application settings.

    Cached for performance across requests.
    """
    return get_settings()


# ==================================================
# Service dependencies
# ==================================================

@lru_cache
def get_task_service(session: Session = Depends(get_db_session)) -> TaskService:
    """
    Returns a TaskService instance wired with a database session.

    Ensures all TaskService operations persist to the DB.
    """
    return TaskService(session=session)


@lru_cache
def get_agent_service() -> AgentService:
    """
    Returns a singleton AgentService instance.
    """
    return AgentService()


@lru_cache
def get_planner_agent() -> PlannerAgent:
    """
    Returns a singleton PlannerAgent instance.
    """
    return PlannerAgent()


@lru_cache
def get_tool_registry() -> ToolRegistry:
    """
    Returns a singleton ToolRegistry instance.
    """
    return ToolRegistry()


@lru_cache
def get_memory_writer() -> MemoryWriter:
    """
    Returns a singleton MemoryWriter instance.
    """
    return MemoryWriter()


@lru_cache
def get_tool_execution_engine(tool_registry: ToolRegistry = Depends(get_tool_registry)) -> ToolExecutionEngine:
    """
    Returns a ToolExecutionEngine instance wired with ToolRegistry.
    """
    return ToolExecutionEngine(tool_registry=tool_registry)


@lru_cache
def get_orchestrator(
    task_service: TaskService = Depends(get_task_service),
    agent_service: AgentService = Depends(get_agent_service),
    tool_registry: ToolRegistry = Depends(get_tool_registry),
    memory_writer: MemoryWriter = Depends(get_memory_writer),
    planner_agent: PlannerAgent = Depends(get_planner_agent),
) -> OrchestratorService:
    """
    Returns a fully wired OrchestratorService instance.

    Dependencies:
    - TaskService: handles persistence
    - AgentService: executes agents
    - ToolRegistry: tracks available tools
    - MemoryWriter: writes memory to storage
    - PlannerAgent: generates execution plans
    """
    return OrchestratorService(
        task_service=task_service,
        agent_service=agent_service,
        tool_registry=tool_registry,
        memory_writer=memory_writer,
        planner_agent=planner_agent,
    )
