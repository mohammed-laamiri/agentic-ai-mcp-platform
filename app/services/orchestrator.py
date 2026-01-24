from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate, TaskRead
from app.services.task_service import TaskService
from app.services.agent_service import AgentService


class OrchestratorService:
    """
    Coordinates agents and tasks.
    """

    def __init__(
        self,
        task_service: TaskService,
        agent_service: AgentService,
    ):
        self.task_service = task_service
        self.agent_service = agent_service

    def run(self, agent: AgentRead, task_in: TaskCreate) -> TaskRead:
        """
        High-level execution flow.
        """
        task = self.task_service.create_task(task_in)

        try:
            task = self.agent_service.execute(agent, task)
        except Exception as exc:
            return self.task_service.fail_task(task, str(exc))

        return task
