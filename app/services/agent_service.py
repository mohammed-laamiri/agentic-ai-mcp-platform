from app.schemas.agent import AgentRead
from app.schemas.task import TaskRead


class AgentService:
    """
    Abstract agent execution layer.
    """

    def execute(self, agent: AgentRead, task: TaskRead) -> TaskRead:
        """
        Execute a task using an agent.

        This method will later:
        - Call LangGraph
        - Invoke MCP tools
        - Use Bedrock models

        For now, it's a placeholder.
        """
        raise NotImplementedError("Agent execution not implemented yet")
