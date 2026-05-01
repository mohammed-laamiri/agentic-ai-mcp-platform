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
from app.services.memory_writer import MemoryWriter

# Execution layer
from app.services.execution.execution_service import ExecutionService

# Tool layer
from app.services.tool_registry import ToolRegistry
from app.services.tool_execution_engine import ToolExecutionEngine

# Runtime singletons (CRITICAL)
from app.runtime.runtime import tool_registry, tool_execution_engine


# =====================================================
# Application Settings
# =====================================================

@lru_cache
def get_app_settings() -> Settings:
    return Settings()


# =====================================================
# Tool Runtime Singletons (FIXES YOUR ERROR)
# =====================================================

def get_tool_registry() -> ToolRegistry:
    return tool_registry


def get_tool_execution_engine() -> ToolExecutionEngine:
    return tool_execution_engine


# =====================================================
# RAG Service Singleton
# =====================================================

_rag_service = RAGService()


def get_rag_service() -> RAGService:
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
# Execution Layer (IMPORTANT FIX)
# =====================================================

@lru_cache
def get_execution_service() -> ExecutionService:
    """
    Execution dispatcher singleton.
    IMPORTANT: ExecutionService takes NO args
    """
    return ExecutionService()


# =====================================================
# Orchestrator (TOP LEVEL)
# =====================================================

@lru_cache
def get_memory_writer() -> MemoryWriter:
    return MemoryWriter()


@lru_cache
def get_orchestrator() -> OrchestratorService:
    return OrchestratorService(
        task_service=get_task_service(),
        agent_service=get_agent_service(),
        planner_agent=get_planner_agent(),
        execution_service=get_execution_service(),
    )