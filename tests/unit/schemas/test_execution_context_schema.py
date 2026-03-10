"""
Unit tests for ExecutionContext in execution_context.py.

Covers set_variable, get_variable, add_agent_output, add_tool_output,
and variables, agent_outputs, tool_outputs properties.
"""

from app.schemas.execution_context import ExecutionContext


def test_set_variable_and_get_variable():
    """set_variable and get_variable round-trip."""
    ctx = ExecutionContext(task_id="t1", user_input="hello")
    ctx.set_variable("key", "value")
    assert ctx.get_variable("key") == "value"
    assert ctx.get_variable("missing", default=99) == 99


def test_add_agent_output():
    """add_agent_output stores and agent_outputs exposes it."""
    ctx = ExecutionContext(task_id="t1", user_input="hi")
    ctx.add_agent_output("agent1", "result1")
    assert ctx.agent_outputs == {"agent1": "result1"}


def test_add_tool_output():
    """add_tool_output stores and tool_outputs exposes it."""
    ctx = ExecutionContext(task_id="t1", user_input="hi")
    ctx.add_tool_output("tool1", {"output": 42})
    assert ctx.tool_outputs == {"tool1": {"output": 42}}


def test_variables_property():
    """variables returns a copy of _variables."""
    ctx = ExecutionContext(task_id="t1", user_input="hi")
    ctx.set_variable("a", 1)
    assert ctx.variables == {"a": 1}
