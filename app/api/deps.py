from app.services.planner_agent import PlannerAgent
from app.services.task_service import TaskService
from app.services.agent_service import AgentService
from app.services.orchestrator import OrchestratorService


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
