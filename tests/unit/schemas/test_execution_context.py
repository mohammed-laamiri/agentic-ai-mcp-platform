"""
Unit tests for ExecutionContext (context.py).

Covers session_id, optional fields, and model_dump.
"""

from app.schemas.context import ExecutionContext


def test_execution_context_required_session_id():
    """ExecutionContext requires session_id."""
    ctx = ExecutionContext(session_id="s1")
    assert ctx.session_id == "s1"
    assert ctx.execution_id is not None


def test_execution_context_with_strategy_and_metadata():
    """ExecutionContext accepts strategy and metadata."""
    ctx = ExecutionContext(
        session_id="s1",
        user_id="u1",
        strategy="MULTI_AGENT",
        metadata={"key": "value"},
    )
    assert ctx.strategy == "MULTI_AGENT"
    assert ctx.metadata == {"key": "value"}
