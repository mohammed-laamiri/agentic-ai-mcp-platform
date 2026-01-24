import uuid
from app.schemas.task import TaskCreate, TaskRead, TaskStatus


class TaskService:
    """
    Manages task lifecycle.
    """

    def create_task(self, task_in: TaskCreate) -> TaskRead:
        """
        Create a new task in PENDING state.
        """
        return TaskRead(
            id=str(uuid.uuid4()),
            input=task_in.input,
            status=TaskStatus.PENDING,
        )

    def complete_task(self, task: TaskRead, output: str) -> TaskRead:
        """
        Mark a task as completed.
        """
        task.status = TaskStatus.COMPLETED
        task.output = output
        return task

    def fail_task(self, task: TaskRead, error: str) -> TaskRead:
        """
        Mark a task as failed.
        """
        task.status = TaskStatus.FAILED
        task.output = error
        return task
