"""
Unit tests for ToolValidator.

Tests validation of tool existence and argument schemas.
"""

import pytest
from unittest.mock import MagicMock

from app.schemas.tool_call import ToolCall
from app.services.tool_validator import ToolValidator, ToolValidationError
from app.services.tool_registry import ToolRegistry, ToolMetadata


@pytest.fixture
def registry():
    """Create a registry with a test tool."""
    reg = ToolRegistry()
    reg.register_tool(
        ToolMetadata(
            tool_id="test_tool",
            name="Test Tool",
            version="1.0",
            description="A test tool",
        )
    )
    # Add mock method for get_input_schema (not in base registry)
    reg.get_input_schema = MagicMock(return_value=None)
    return reg


@pytest.fixture
def validator(registry):
    return ToolValidator(registry)


def test_validate_existing_tool(validator):
    """Validation should pass for registered tool."""
    call = ToolCall(tool_id="test_tool", arguments={})
    # Should not raise (no schema = accepts all)
    validator.validate(call)


def test_validate_unregistered_tool_raises(validator):
    """Validation should fail for unregistered tool."""
    call = ToolCall(tool_id="nonexistent", arguments={})

    with pytest.raises(ToolValidationError) as exc_info:
        validator.validate(call)

    assert "not registered" in str(exc_info.value)


def test_validate_with_schema_missing_required():
    """Validation should fail when required field is missing."""
    registry = ToolRegistry()
    registry.register_tool(
        ToolMetadata(
            tool_id="schema_tool",
            name="Schema Tool",
            version="1.0",
            description="Tool with schema",
        )
    )
    # Mock get_input_schema to return a schema
    registry.get_input_schema = MagicMock(return_value={
        "required": ["message"],
        "properties": {
            "message": {"type": "string"}
        }
    })

    validator = ToolValidator(registry)
    call = ToolCall(tool_id="schema_tool", arguments={})

    with pytest.raises(ToolValidationError) as exc_info:
        validator.validate(call)

    assert "missing required argument 'message'" in str(exc_info.value)


def test_validate_with_schema_wrong_string_type():
    """Validation should fail when string field gets wrong type."""
    registry = ToolRegistry()
    registry.register_tool(
        ToolMetadata(
            tool_id="typed_tool",
            name="Typed Tool",
            version="1.0",
            description="Tool with typed schema",
        )
    )
    registry.get_input_schema = MagicMock(return_value={
        "required": [],
        "properties": {
            "message": {"type": "string"}
        }
    })

    validator = ToolValidator(registry)
    call = ToolCall(tool_id="typed_tool", arguments={"message": 123})

    with pytest.raises(ToolValidationError) as exc_info:
        validator.validate(call)

    assert "must be string" in str(exc_info.value)


def test_validate_with_schema_wrong_integer_type():
    """Validation should fail when integer field gets wrong type."""
    registry = ToolRegistry()
    registry.register_tool(
        ToolMetadata(
            tool_id="int_tool",
            name="Int Tool",
            version="1.0",
            description="Tool with int schema",
        )
    )
    registry.get_input_schema = MagicMock(return_value={
        "required": [],
        "properties": {
            "count": {"type": "integer"}
        }
    })

    validator = ToolValidator(registry)
    call = ToolCall(tool_id="int_tool", arguments={"count": "not_an_int"})

    with pytest.raises(ToolValidationError) as exc_info:
        validator.validate(call)

    assert "must be integer" in str(exc_info.value)


def test_validate_with_schema_wrong_number_type():
    """Validation should fail when number field gets wrong type."""
    registry = ToolRegistry()
    registry.register_tool(
        ToolMetadata(
            tool_id="num_tool",
            name="Num Tool",
            version="1.0",
            description="Tool with number schema",
        )
    )
    registry.get_input_schema = MagicMock(return_value={
        "required": [],
        "properties": {
            "value": {"type": "number"}
        }
    })

    validator = ToolValidator(registry)
    call = ToolCall(tool_id="num_tool", arguments={"value": "not_a_number"})

    with pytest.raises(ToolValidationError) as exc_info:
        validator.validate(call)

    assert "must be number" in str(exc_info.value)


def test_validate_with_schema_number_accepts_int():
    """Number type should accept integers."""
    registry = ToolRegistry()
    registry.register_tool(
        ToolMetadata(
            tool_id="num_tool",
            name="Num Tool",
            version="1.0",
            description="Tool with number schema",
        )
    )
    registry.get_input_schema = MagicMock(return_value={
        "required": [],
        "properties": {
            "value": {"type": "number"}
        }
    })

    validator = ToolValidator(registry)
    call = ToolCall(tool_id="num_tool", arguments={"value": 42})

    # Should not raise
    validator.validate(call)


def test_validate_with_schema_wrong_boolean_type():
    """Validation should fail when boolean field gets wrong type."""
    registry = ToolRegistry()
    registry.register_tool(
        ToolMetadata(
            tool_id="bool_tool",
            name="Bool Tool",
            version="1.0",
            description="Tool with boolean schema",
        )
    )
    registry.get_input_schema = MagicMock(return_value={
        "required": [],
        "properties": {
            "flag": {"type": "boolean"}
        }
    })

    validator = ToolValidator(registry)
    call = ToolCall(tool_id="bool_tool", arguments={"flag": "true"})

    with pytest.raises(ToolValidationError) as exc_info:
        validator.validate(call)

    assert "must be boolean" in str(exc_info.value)


def test_validate_with_schema_wrong_object_type():
    """Validation should fail when object field gets wrong type."""
    registry = ToolRegistry()
    registry.register_tool(
        ToolMetadata(
            tool_id="obj_tool",
            name="Obj Tool",
            version="1.0",
            description="Tool with object schema",
        )
    )
    registry.get_input_schema = MagicMock(return_value={
        "required": [],
        "properties": {
            "data": {"type": "object"}
        }
    })

    validator = ToolValidator(registry)
    call = ToolCall(tool_id="obj_tool", arguments={"data": "not_an_object"})

    with pytest.raises(ToolValidationError) as exc_info:
        validator.validate(call)

    assert "must be object" in str(exc_info.value)


def test_validate_with_schema_wrong_array_type():
    """Validation should fail when array field gets wrong type."""
    registry = ToolRegistry()
    registry.register_tool(
        ToolMetadata(
            tool_id="arr_tool",
            name="Arr Tool",
            version="1.0",
            description="Tool with array schema",
        )
    )
    registry.get_input_schema = MagicMock(return_value={
        "required": [],
        "properties": {
            "items": {"type": "array"}
        }
    })

    validator = ToolValidator(registry)
    call = ToolCall(tool_id="arr_tool", arguments={"items": "not_an_array"})

    with pytest.raises(ToolValidationError) as exc_info:
        validator.validate(call)

    assert "must be array" in str(exc_info.value)


def test_validate_without_schema():
    """Validation should pass when no schema is defined."""
    registry = ToolRegistry()
    registry.register_tool(
        ToolMetadata(
            tool_id="no_schema_tool",
            name="No Schema Tool",
            version="1.0",
            description="Tool without schema",
        )
    )
    registry.get_input_schema = MagicMock(return_value=None)

    validator = ToolValidator(registry)
    call = ToolCall(tool_id="no_schema_tool", arguments={"anything": "goes"})

    # Should not raise
    validator.validate(call)


def test_validate_extra_fields_allowed():
    """Extra fields not in schema should be allowed."""
    registry = ToolRegistry()
    registry.register_tool(
        ToolMetadata(
            tool_id="flexible_tool",
            name="Flexible Tool",
            version="1.0",
            description="Tool that allows extras",
        )
    )
    registry.get_input_schema = MagicMock(return_value={
        "required": ["name"],
        "properties": {
            "name": {"type": "string"}
        }
    })

    validator = ToolValidator(registry)
    call = ToolCall(tool_id="flexible_tool", arguments={
        "name": "test",
        "extra_field": "allowed"
    })

    # Should not raise
    validator.validate(call)
