import pytest
from app.services.tool_registry import ToolRegistry, ToolMetadata
from app.services.tool_execution_engine import ToolExecutionEngine
from app.schemas.tool_call import ToolCall

# -----------------------------
# Test tool: simple echo tool
# -----------------------------

def echo_tool(message: str) -> str:
    return f"Echo: {message}"


@pytest.fixture
def tool_registry() -> ToolRegistry:
    """Provide a fresh ToolRegistry."""
    registry = ToolRegistry()

    # Register echo tool
    registry.register_tool(
        ToolMetadata(
            tool_id="echo_tool",
            name="Echo Tool",
            version="1.0",
            description="Echoes the input message",
        ),
        callable_fn=echo_tool,
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
    # Prepare tool call
    call = ToolCall(tool_id="echo_tool", arguments={"message": "hello world"})

    # Execute
    result = tool_engine.execute(call)

    # Assertions
    assert result.status == "success"
    assert result.output == "Echo: hello world"
    assert result.error is None