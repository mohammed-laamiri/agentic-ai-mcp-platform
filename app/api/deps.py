from app.services.planner_agent import PlannerAgent
from app.services.task_service import TaskService
from app.services.agent_service import AgentService
from app.services.orchestrator import OrchestratorService
from app.services.tool_registry import ToolRegistry
from app.services.tool_executor import ToolExecutor


def get_task_service() -> TaskService:
    return TaskService()


def get_agent_service() -> AgentService:
    return AgentService()


def get_planner_agent() -> PlannerAgent:
    return PlannerAgent()


def get_tool_executor() -> ToolExecutor:
    return ToolExecutor()


def get_orchestrator() -> OrchestratorService:
    return OrchestratorService(
        task_service=get_task_service(),
        agent_service=get_agent_service(),
        planner_agent=get_planner_agent(),
        tool_executor=get_tool_executor(),
    )


def get_tool_registry() -> ToolRegistry:
    return ToolRegistry()
