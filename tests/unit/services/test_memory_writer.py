"""
Unit tests for MemoryWriter.

Covers get, list_records, and clear.
"""

from app.services.memory_writer import MemoryWriter
from app.schemas.execution import ExecutionResult
from app.schemas.agent_execution_context import AgentExecutionContext


def test_memory_writer_get_returns_record():
    """get returns a previously written record by record_id."""
    writer = MemoryWriter()
    result = ExecutionResult(execution_id="e1", output="out", status="SUCCESS")
    context = AgentExecutionContext()
    record_id = writer.write(execution_result=result, agent_context=context)
    got = writer.get(record_id)
    assert got is not None
    assert got["execution_id"] == "e1"


def test_memory_writer_get_returns_none_when_missing():
    """get returns None when record_id does not exist."""
    writer = MemoryWriter()
    assert writer.get("nonexistent-id") is None


def test_memory_writer_list_records():
    """list_records returns all stored records."""
    writer = MemoryWriter()
    result = ExecutionResult(execution_id="e1", status="SUCCESS")
    context = AgentExecutionContext()
    writer.write(execution_result=result, agent_context=context)
    writer.write(execution_result=result, agent_context=context)
    records = writer.list_records()
    assert len(records) == 2


def test_memory_writer_clear():
    """clear removes all records."""
    writer = MemoryWriter()
    result = ExecutionResult(execution_id="e1", status="SUCCESS")
    context = AgentExecutionContext()
    rid = writer.write(execution_result=result, agent_context=context)
    writer.clear()
    assert writer.get(rid) is None
    assert writer.list_records() == []
