"""
Memory Writer Service.

Responsible for persisting execution-level traces for future
retrieval, auditing, or episodic memory.

Architectural role:
- Snapshot ExecutionResult + AgentExecutionContext
- Optional session-level ExecutionContext
- Storage-agnostic (in-memory first, extendable)
- Append-only, non-mutating
- Observability hooks (timestamps, correlation IDs)

Future enhancements:
- DynamoDB / OpenSearch backend
- Batch writes
- Replay & event sourcing
- Cost / latency tracking
"""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from uuid import uuid4

from app.schemas.execution import ExecutionResult
from app.schemas.execution_context import ExecutionContext
from app.schemas.agent_execution_context import AgentExecutionContext


class MemoryWriter:
    """
    Memory Writer – stores execution traces for auditing, replay, and reflection.
    """

    def __init__(self) -> None:
        # In-memory store (temporary, replaceable)
        # Key: run_id / execution_id, Value: serialized record
        self._store: Dict[str, Dict[str, Any]] = {}

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def write(
        self,
        execution_result: ExecutionResult,
        agent_context: AgentExecutionContext,
        session_context: Optional[ExecutionContext] = None,
    ) -> str:
        """
        Persist a snapshot of an execution.

        Args:
            execution_result: The output of the agent orchestration
            agent_context: Runtime-scoped ephemeral context
            session_context: Optional session-level context

        Returns:
            record_id: Unique identifier for this memory record
        """
        record_id = str(uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        # Compose memory record
        record: Dict[str, Any] = {
            "record_id": record_id,
            "timestamp": timestamp,
            "execution_id": getattr(execution_result, "execution_id", None),
            "task_id": getattr(execution_result, "task_id", None),
            "agent_id": getattr(execution_result, "agent_id", None),
            "agent_name": getattr(execution_result, "agent_name", None),
            "strategy": getattr(execution_result, "strategy", None),
            "input": getattr(execution_result, "input", None),
            "output": getattr(execution_result, "output", None),
            "status": getattr(execution_result, "status", None),
            "tool_calls": [tc.dict() for tc in getattr(agent_context, "tool_calls", [])],
            "child_results": getattr(execution_result, "child_results", None),
            "errors": getattr(execution_result, "errors", None),
            "metadata": getattr(execution_result, "metadata", None),
            "session_context": session_context.dict() if session_context else None,
            "started_at": getattr(execution_result, "started_at", None),
            "finished_at": getattr(execution_result, "finished_at", None),
        }

        # Store in memory (append-only)
        self._store[record_id] = record

        # Observability / debug hook
        print(f"[MemoryWriter] Stored execution record: {record_id}")

        return record_id

    # --------------------------------------------------
    # Retrieval (optional / for inspection)
    # --------------------------------------------------

    def get(self, record_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a stored memory record by ID.

        Returns None if not found.
        """
        return self._store.get(record_id)

    def list_records(self) -> List[Dict[str, Any]]:
        """
        Return all stored memory records.
        """
        return list(self._store.values())

    def clear(self) -> None:
        """
        Clear all stored records (useful for tests or reset).
        """
        self._store.clear()
