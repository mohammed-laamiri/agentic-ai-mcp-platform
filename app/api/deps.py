"""
Dependency injection container.

Provides singleton access to core services.
"""

from functools import lru_cache

from app.core.config import Settings

from app.services.rag.rag_service import RAGService
from app.services.task_service import TaskService
from app.services.agent_service import AgentService
from app.services.planner_agent import PlannerAgent
from app.services.orchestrator import OrchestratorService

from app.services.tool_registry import ToolRegistry
from app.services.tool_execution_engine import ToolExecutionEngine

# Import runtime singletons
from app.runtime.runtime import tool_registry, tool_execution_engine


# =====================================================
# Application Settings
# =====================================================

@lru_cache
def get_app_settings() -> Settings:
    """
    Returns application settings singleton.
    """
    return Settings()


# =====================================================
# Core Domain Services
# =====================================================

def get_task_service() -> TaskService:
    return TaskService()


def get_agent_service() -> AgentService:
    return AgentService()


def get_planner_agent() -> PlannerAgent:
    return PlannerAgent()


def get_orchestrator() -> OrchestratorService:
    return OrchestratorService(
        task_service=get_task_service(),
        agent_service=get_agent_service(),
        planner_agent=get_planner_agent(),
    )


# =====================================================
# Tool Runtime Singletons
# =====================================================

def get_tool_registry() -> ToolRegistry:
    return tool_registry


def get_tool_execution_engine() -> ToolExecutionEngine:
    return tool_execution_engine

# =====================================================
# RAG Service Singleton
# =====================================================

rag_service = RAGService()


def get_rag_service() -> RAGService:
    return rag_service