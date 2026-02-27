"""
MultiAgentExecutor

Executes multiple agents sequentially as defined in the execution plan.

Responsibilities:
- Execute agents in order
- Pass output of each agent to the next
- Maintain shared execution context
- Return standardized execution result

Non-responsibilities:
- Does NOT decide execution strategy (Planner does)
- Does NOT orchestrate workflow (OrchestratorService does)
"""

from typing import Any, Dict, List


class MultiAgentExecutor:
    """
    Executes multiple agents sequentially.

    Contract:
        agents: List of agent instances implementing:
            execute(task_in: Any, context: Dict[str, Any]) -> Dict[str, Any]

        task_in: Initial task input

        context: Shared mutable execution context

    Returns:
        Dict[str, Any]: Standard execution result
    """

    def execute(
        self,
        agents: List[Any],
        task_in: Any,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute agents sequentially.

        Each agent receives:
            - task_in: output from previous agent
            - context: shared execution context

        Returns standardized execution result.
        """

        if not agents:
            return {
                "success": False,
                "strategy": "multi_agent",
                "error": "No agents provided",
                "steps_executed": 0,
                "results": [],
                "final_result": None,
            }

        results: List[Dict[str, Any]] = []
        current_input: Any = task_in

        try:
            for index, agent in enumerate(agents):

                if not hasattr(agent, "execute"):
                    raise AttributeError(
                        f"Agent at index {index} does not implement execute()"
                    )

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

        except Exception as e:
            return {
                "success": False,
                "strategy": "multi_agent",
                "error": str(e),
                "steps_executed": len(results),
                "results": results,
                "final_result": None,
            }