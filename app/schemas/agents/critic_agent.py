# app/agents/critic_agent.py

"""
Critic Agent (Reflector Stub)

Purpose:
- Reviews execution results
- Provides feedback
- Can later improve plans or trigger retries

This is a SAFE MVP stub implementation.
It does NOT modify execution yet.
"""

from datetime import datetime, timezone
from typing import Optional

from app.schemas.execution import ExecutionResult


class CriticFeedback:
    """
    Feedback produced by the Critic Agent.
    """

    def __init__(
        self,
        success: bool,
        feedback: str,
        suggested_retry: bool = False,
        improved_prompt: Optional[str] = None,
    ):
        self.success = success
        self.feedback = feedback
        self.suggested_retry = suggested_retry
        self.improved_prompt = improved_prompt
        self.timestamp = datetime.now(timezone.utc)

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "feedback": self.feedback,
            "suggested_retry": self.suggested_retry,
            "improved_prompt": self.improved_prompt,
            "timestamp": self.timestamp.isoformat(),
        }


class CriticAgent:
    """
    MVP Critic Agent.

    Responsibilities:
    - Analyze ExecutionResult
    - Provide feedback
    - Suggest retry if failed

    Future versions can:
    - Improve prompts
    - Trigger re-planning
    - Score execution quality
    """

    async def review(
        self,
        result: ExecutionResult,
    ) -> CriticFeedback:
        """
        Review execution result and produce feedback.
        """

        # Successful execution
        if result.success:
            return CriticFeedback(
                success=True,
                feedback="Execution successful. No issues detected.",
                suggested_retry=False,
            )

        # Failed execution
        return CriticFeedback(
            success=False,
            feedback=f"Execution failed: {result.error}",
            suggested_retry=True,
            improved_prompt=None,
        )