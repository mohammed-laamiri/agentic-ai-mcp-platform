"""
Dependency injection container.

Provides singleton access to core services.

Architecture guarantees:
- Singleton lifecycle for core services
- Clean dependency graph
- Compatible with MCP Tool Layer
"""

from functools import lru_cache

from app.core.config import Settings

# Core services
from app.services.rag.rag_service import RAGService
from app.services.task_service import TaskService
from app.services.agent_service import AgentService
from app.services.planner_agent import PlannerAgent
from app.services.orchestrator import OrchestratorService

# Execution layer
from app.services.execution.execution_service import ExecutionService

# Tool layer
from app.services.tool_registry import ToolRegistry
from app.services.tool_execution_engine import ToolExecutionEngine

# Runtime singletons
from app.runtime.runtime import tool_registry, tool_execution_engine


# =====================================================
# Application Settings
# =====================================================

@lru_cache
def get_app_settings() -> Settings:
    """
    Application settings singleton.
    """
    return Settings()


# =====================================================
# Tool Runtime Singletons
# =====================================================

def get_tool_registry() -> ToolRegistry:
    """
    Global ToolRegistry singleton.
    """
    return tool_registry


def get_tool_execution_engine() -> ToolExecutionEngine:
    """
    Global ToolExecutionEngine singleton.
    """
    return tool_execution_engine


# =====================================================
# RAG Service Singleton
# =====================================================

_rag_service = RAGService()


def get_rag_service() -> RAGService:
    """
    Global RAG service singleton.
    """
    return _rag_service


# =====================================================
# Core Services
# =====================================================

@lru_cache
def get_task_service() -> TaskService:
    return TaskService()


@lru_cache
def get_agent_service() -> AgentService:
    return AgentService(
        rag_service=get_rag_service(),
    )


@lru_cache
def get_planner_agent() -> PlannerAgent:
    return PlannerAgent(
        rag_service=get_rag_service(),
    )


# =====================================================
# Execution Layer
# =====================================================

@lru_cache
def get_execution_service() -> ExecutionService:
    """
    Execution dispatcher singleton.
    """
    return ExecutionService(
        agent_service=get_agent_service(),
        tool_engine=get_tool_execution_engine(),  # ← FIXED
    )


# =====================================================
# Orchestrator (TOP LEVEL)
# =====================================================

@lru_cache
def get_orchestrator() -> OrchestratorService:
    """
    Top-level orchestrator singleton.
    """
    return OrchestratorService(
        task_service=get_task_service(),
        agent_service=get_agent_service(),
        planner_agent=get_planner_agent(),
        execution_service=get_execution_service(),
    )