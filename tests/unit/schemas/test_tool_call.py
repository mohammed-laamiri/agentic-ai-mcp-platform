"""
Unit tests for ToolCall schema.

Covers validators, ensure_call_id, and to_mcp_dict.
"""

import pytest

from app.schemas.tool_call import ToolCall


def test_validate_tool_id_empty_raises():
    """tool_id cannot be empty."""
    with pytest.raises(ValueError, match="tool_id must be non-empty"):
        ToolCall(tool_id="", arguments={})


def test_validate_tool_id_whitespace_raises():
    """tool_id cannot be only whitespace."""
    with pytest.raises(ValueError, match="tool_id must be non-empty"):
        ToolCall(tool_id="   ", arguments={})


def test_normalize_call_id_none():
    """call_id None remains None."""
    c = ToolCall(tool_id="t", arguments={}, call_id=None)
    assert c.call_id is None


def test_normalize_call_id_converts_to_str():
    """call_id is normalized to string."""
    c = ToolCall(tool_id="t", arguments={}, call_id=123)
    assert c.call_id == "123"


def test_ensure_call_id_sets_uuid_when_missing():
    """ensure_call_id sets call_id when it was None."""
    c = ToolCall(tool_id="t", arguments={})
    assert c.call_id is None
    got = c.ensure_call_id()
    assert got is not None
    assert c.call_id == got


def test_ensure_call_id_returns_existing():
    """ensure_call_id returns existing call_id when set."""
    c = ToolCall(tool_id="t", arguments={}, call_id="existing-123")
    assert c.ensure_call_id() == "existing-123"


def test_to_mcp_dict():
    """to_mcp_dict returns MCP-safe dict."""
    c = ToolCall(tool_id="my_tool", arguments={"a": 1}, call_id="cid")
    d = c.to_mcp_dict()
    assert d == {"tool_id": "my_tool", "arguments": {"a": 1}, "call_id": "cid"}
