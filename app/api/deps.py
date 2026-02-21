"""
Dependency injection container.

Provides singleton access to core services.

IMPORTANT:
Uses the same ToolRegistry and ToolExecutionEngine
instances created in main.py
"""

from app.services.task_service import TaskService
from app.services.agent_service import AgentService
from app.services.planner_agent import PlannerAgent
from app.services.orchestrator import OrchestratorService

from app.services.tool_registry import ToolRegistry
from app.services.tool_execution_engine import ToolExecutionEngine

# Import runtime singletons
from app.main import (
    tool_registry,
    tool_execution_engine,
)


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