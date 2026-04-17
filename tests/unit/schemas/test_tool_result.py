"""
Unit tests for ToolResult schema.

Covers is_error, has_output, and to_log_dict.
"""

from app.schemas.tool_result import ToolResult


def test_is_error_true_when_success_false():
    """is_error is True when success is False."""
    r = ToolResult(tool_id="t", success=False, error="e")
    assert r.is_error is True


def test_is_error_false_when_success_true():
    """is_error is False when success is True."""
    r = ToolResult(tool_id="t", success=True, output="ok")
    assert r.is_error is False


def test_has_output_true_when_output_set():
    """has_output is True when output is not None."""
    r = ToolResult(tool_id="t", success=True, output="data")
    assert r.has_output is True


def test_has_output_false_when_output_none():
    """has_output is False when output is None."""
    r = ToolResult(tool_id="t", success=False, output=None)
    assert r.has_output is False


def test_to_log_dict():
    """to_log_dict returns log-safe representation."""
    r = ToolResult(
        tool_id="t",
        success=True,
        error=None,
        execution_id="e1",
        retries=0,
        metadata={"k": "v"},
    )
    d = r.to_log_dict()
    assert d["tool_id"] == "t"
    assert d["success"] is True
    assert d["execution_id"] == "e1"
    assert d["metadata"] == {"k": "v"}
