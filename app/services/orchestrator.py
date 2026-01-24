"""
Orchestrator service.

This layer is responsible for coordinating high-level workflows
without owning business logic or execution details.

Think of this service as the "conductor":
- It knows *what happens next*
- It does NOT know *how* things are implemented internally

Current responsibilities:
- Coordinate agent execution
- Coordinate task lifecycle creation
- Create and own the execution context

Future responsibilities (by design):
- Planning vs execution separation
- Multi-agent orchestration
- LangGraph flows
- MCP tool invocation
- Retries, reflection, and recovery
"""

from app.schemas.agent import AgentRead
from app.schemas.task import TaskCreate, TaskRead
from app.schemas.execution import ExecutionResult
from app.schemas.agent_execution_context import AgentExecutionContext
from app.services.agent_service import AgentService
from app.services.task_service import TaskService


class OrchestratorService:
    """
    High-level workflow coordinator.

    This service SHOULD:
    - Know the sequence of steps
    - Delegate real work to domain services
    - Remain thin, readable, and predictable

    This service SHOULD NOT:
    - Contain execution logic
    - Contain persistence logic
    - Know how agents internally work
    """

    def __init__(
        self,
        task_service: TaskService,
        agent_service: AgentService,
    ) -> None:
        """
        Initialize the orchestrator with required domain services.

        Dependency injection is intentional:
        - Enables clean unit testing
        - Prevents tight coupling
        - Allows future swapping (mock agents, async agents, etc.)
        """
        self._task_service = task_service
        self._agent_service = agent_service

    def run(self, agent: AgentRead, task_in: TaskCreate) -> TaskRead:
        """
        Run a task using an agent.

        High-level workflow:
        1. Create execution context
        2. Plan the execution (stub for now)
        3. Execute the task using an agent
        4. Persist the resulting task state

        IMPORTANT:
        This method intentionally does NOT:
        - Handle retries
        - Catch failures
        - Perform branching logic

        Those behaviors belong in later steps and
        will be introduced incrementally.
        """

        # ==================================================
        # Step 0: Create execution context
        # ==================================================
        # The orchestrator owns this object.
        # Agents may observe it, but must not mutate it.
        context = AgentExecutionContext()

        # ==========================
        # Step 1: Planning phase
        # ==========================
        # Currently a no-op stub, but exists for architectural clarity.
        execution_plan = self._plan(
            agent=agent,
            task_in=task_in,
            context=context,
        )

        # ==========================
        # Step 2: Execution phase
        # ==========================
        execution_result: ExecutionResult = self._execute(
            agent=agent,
            task_in=task_in,
            plan=execution_plan,
            context=context,
        )

        # ==========================
        # Step 3: Persistence phase
        # ==========================
        return self._task_service.create(
            task_in=task_in,
            execution_result=execution_result.model_dump(),
        )

    # ============================================================
    # Internal orchestration steps
    # ============================================================

    def _plan(
        self,
        agent: AgentRead,
        task_in: TaskCreate,
        context: AgentExecutionContext,
    ) -> dict:
        """
        Planning phase (STUB).

        Purpose:
        - Decide which agents to call
        - Determine execution strategy
        - Prepare tool invocation graph

        Current behavior:
        - Returns an empty plan
        - Context is not used yet

        Why context is passed now:
        - Prevents signature churn later
        - Makes orchestration intent explicit
        """
        return {}

    def _execute(
        self,
        agent: AgentRead,
        task_in: TaskCreate,
        plan: dict,
        context: AgentExecutionContext,
    ) -> ExecutionResult:
        """
        Execution phase.

        Purpose:
        - Execute the task using the selected agent(s)
        - Return a typed execution result

        Current behavior:
        - Delegates directly to AgentService
        - Ignores plan and context for now

        Future behavior:
        - Execute multi-step plans
        - Call multiple agents
        - Use MCP tools
        """
        return self._agent_service.execute(
            agent=agent,
            task=task_in,
            context=context,
        )
