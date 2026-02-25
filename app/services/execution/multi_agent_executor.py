"""
MultiAgentExecutor

Executes multiple agents sequentially as defined in the execution plan.

This executor is responsible ONLY for execution.
It does NOT decide strategy (Planner does that).
It does NOT handle orchestration (OrchestratorService does that).

It simply runs agents in order.
"""

from typing import Any, Dict, List


class MultiAgentExecutor:
    """
    Executes multiple agents sequentially.

    Contract:
    - agents: list of agent instances
    - task_in: the task input
    - context: shared execution context
    """

    def execute(
        self,
        agents: List[Any],
        task_in: Any,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute agents sequentially.

        Returns execution result dictionary.
        """

        results = []
        current_input = task_in

        for agent in agents:
            agent_result = agent.execute(
                task_in=current_input,
                context=context,
            )

            results.append(agent_result)

            # Pass result to next agent
            current_input = agent_result

        return {
            "success": True,
            "strategy": "multi_agent",
            "steps_executed": len(agents),
            "results": results,
            "final_result": current_input,
        }