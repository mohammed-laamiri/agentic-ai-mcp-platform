"""
Execution strategy enum.

Defines the supported execution strategies for task execution.

This enum acts as a contract between:
- PlannerAgent (decides strategy)
- OrchestratorService (interprets strategy)
- Future execution engines
"""

from enum import Enum


class ExecutionStrategy(str, Enum):
    """
    Supported execution strategies.

    Why this exists:
    - Prevents magic strings in orchestration logic
    - Enables safe expansion to multi-agent execution
    - Makes execution plans explicit and type-safe
    """

    SINGLE_AGENT = "single_agent"

    # Future examples (NOT implemented yet):
    # MULTI_AGENT = "multi_agent"
    # TOOL_CHAIN = "tool_chain"
