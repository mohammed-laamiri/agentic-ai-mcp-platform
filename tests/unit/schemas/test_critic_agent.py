"""
Unit tests for Critic Agent.

Tests CriticFeedback and CriticAgent classes.
"""

import pytest

from app.schemas.agents.critic_agent import CriticFeedback, CriticAgent
from app.schemas.execution import ExecutionResult


class TestCriticFeedback:
    """Tests for CriticFeedback class."""

    def test_critic_feedback_init(self):
        """CriticFeedback should initialize with all attributes."""
        feedback = CriticFeedback(
            success=True,
            feedback="Test feedback",
            suggested_retry=False,
            improved_prompt=None,
        )

        assert feedback.success is True
        assert feedback.feedback == "Test feedback"
        assert feedback.suggested_retry is False
        assert feedback.improved_prompt is None
        assert feedback.timestamp is not None

    def test_critic_feedback_with_retry(self):
        """CriticFeedback should support retry suggestion."""
        feedback = CriticFeedback(
            success=False,
            feedback="Failed",
            suggested_retry=True,
            improved_prompt="Try again with better prompt",
        )

        assert feedback.success is False
        assert feedback.suggested_retry is True
        assert feedback.improved_prompt == "Try again with better prompt"

    def test_critic_feedback_to_dict(self):
        """CriticFeedback.to_dict should return dict representation."""
        feedback = CriticFeedback(
            success=True,
            feedback="All good",
        )

        result = feedback.to_dict()

        assert isinstance(result, dict)
        assert result["success"] is True
        assert result["feedback"] == "All good"
        assert "timestamp" in result


class TestCriticAgent:
    """Tests for CriticAgent class."""

    @pytest.mark.asyncio
    async def test_critic_agent_review_success(self):
        """CriticAgent.review should return positive feedback for successful result."""
        from unittest.mock import MagicMock

        agent = CriticAgent()

        # Create a mock result with success=True
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.error = None

        feedback = await agent.review(mock_result)

        assert feedback.success is True
        assert "successful" in feedback.feedback.lower()
        assert feedback.suggested_retry is False

    @pytest.mark.asyncio
    async def test_critic_agent_review_failure(self):
        """CriticAgent.review should suggest retry for failed result."""
        from unittest.mock import MagicMock

        agent = CriticAgent()

        # Create a mock result with success=False
        mock_result = MagicMock()
        mock_result.success = False
        mock_result.error = "Something went wrong"

        feedback = await agent.review(mock_result)

        assert feedback.success is False
        assert "failed" in feedback.feedback.lower()
        assert feedback.suggested_retry is True
