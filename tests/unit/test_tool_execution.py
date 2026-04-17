import pytest
from app.services.tool_registry import ToolRegistry, ToolMetadata
from app.services.tool_execution_engine import ToolExecutionEngine
from app.schemas.tool_call import ToolCall
from app.schemas.agent_execution_context import AgentExecutionContext


# -----------------------------
# Test tool: simple echo tool
# -----------------------------

def echo_tool(message: str) -> str:
    return f"Echo: {message}"


@pytest.fixture
def tool_registry() -> ToolRegistry:
    """Provide a fresh ToolRegistry."""
    registry = ToolRegistry()

    # Register echo tool with executor
    registry.register_tool(
        ToolMetadata(
            tool_id="echo_tool",
            name="Echo Tool",
            version="1.0",
            description="Echoes the input message",
        ),
        executor=echo_tool,
    )
    return registry


@pytest.fixture
def tool_engine(tool_registry: ToolRegistry) -> ToolExecutionEngine:
    """Provide ToolExecutionEngine wired with the registry."""
    return ToolExecutionEngine(tool_registry)


# -----------------------------
# Test single tool execution
# -----------------------------

def test_echo_tool_execution(tool_engine: ToolExecutionEngine):
    """Test that a registered tool can be executed via the engine."""
    # Prepare tool call
    call = ToolCall(tool_id="echo_tool", arguments={"message": "hello world"})
    context = AgentExecutionContext()

    # Execute batch (single item)
    results = tool_engine.execute_batch(
        tool_calls=[call],
        context=context,
    )

    # Assertions
    assert len(results) == 1
    result = results[0]
    assert result.success is True
    assert result.output == "Echo: hello world"
    assert result.error is None
