"""
Dependency injection for FastAPI.

Provides singletons for services and runtime components.
"""

from app.services.planner_agent import PlannerAgent
from app.services.task_service import TaskService
from app.services.agent_service import AgentService
from app.services.orchestrator import OrchestratorService
from app.services.tool_registry import ToolRegistry
from app.services.tool_executor import ToolExecutor
from app.services.tool_execution_engine import ToolExecutionEngine

# -------------------------
# Singletons / runtime instances
# -------------------------

tool_registry = ToolRegistry()
tool_executor = ToolExecutor(tool_registry)
tool_execution_engine = ToolExecutionEngine(tool_registry)

task_service = TaskService()
agent_service = AgentService()
planner_agent = PlannerAgent()

# Orchestrator does NOT take tool_executor in the constructor
orchestrator_service = OrchestratorService(
    task_service=task_service,
    agent_service=agent_service,
    planner_agent=planner_agent,
)

# -------------------------
# Dependency getters
# -------------------------

def get_task_service() -> TaskService:
    return task_service

def get_agent_service() -> AgentService:
    return agent_service

def get_planner_agent() -> PlannerAgent:
    return planner_agent

def get_tool_executor() -> ToolExecutor:
    return tool_executor

def get_tool_registry() -> ToolRegistry:
    return tool_registry

def get_tool_execution_engine() -> ToolExecutionEngine:
    return tool_execution_engine

def get_orchestrator() -> OrchestratorService:
    return orchestrator_service