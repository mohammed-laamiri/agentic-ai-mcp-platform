"""
Execution Trace Repository.

Stores detailed execution traces for full observability.

Architectural role:
- Low-level execution tracing
- Agent execution lineage tracking
- Tool execution lineage tracking
- Enables debugging, audit, and observability

Trace granularity levels:
- Run level
- Agent level
- Tool level
- Event level

Storage:
- In-memory (current implementation)
- Pluggable later to DB / Redis / OpenSearch
"""

from typing import Dict, List, Optional, Any
from uuid import uuid4
from datetime import datetime, timezone


class ExecutionTraceRepository:
    """
    Repository responsible for storing execution traces.

    Designed to be:
    - Safe
    - Observable
    - Non-blocking
    - Pluggable
    """

    def __init__(self) -> None:
        self._traces: Dict[str, Dict[str, Any]] = {}

    # ==================================================
    # Core Trace Operations
    # ==================================================

    def create_trace(
        self,
        run_id: str,
        trace_type: str,
        metadata: Optional[Dict[str, Any]] = None,
        parent_trace_id: Optional[str] = None,
    ) -> str:
        """
        Create a new execution trace.

        Args:
            run_id: execution run id
            trace_type: run | agent | tool | event
            metadata: optional metadata
            parent_trace_id: optional parent trace

        Returns:
            trace_id
        """

        trace_id = str(uuid4())

        self._traces[trace_id] = {
            "trace_id": trace_id,
            "run_id": run_id,
            "parent_trace_id": parent_trace_id,
            "trace_type": trace_type,
            "metadata": metadata or {},
            "created_at": datetime.now(timezone.utc),
            "events": [],
        }

        return trace_id

    # ==================================================
    # Event Recording
    # ==================================================

    def add_event(
        self,
        trace_id: str,
        event_type: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Add event to trace timeline.
        """

        trace = self._traces.get(trace_id)

        if trace is None:
            return

        trace["events"].append(
            {
                "event_id": str(uuid4()),
                "event_type": event_type,
                "metadata": metadata or {},
                "timestamp": datetime.now(timezone.utc),
            }
        )

    # ==================================================
    # Completion
    # ==================================================

    def complete_trace(
        self,
        trace_id: str,
        status: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Mark trace as completed.
        """

        trace = self._traces.get(trace_id)

        if trace is None:
            return

        trace["status"] = status
        trace["completed_at"] = datetime.now(timezone.utc)

        if metadata:
            trace["metadata"].update(metadata)

    # ==================================================
    # Query
    # ==================================================

    def get(self, trace_id: str) -> Optional[Dict[str, Any]]:
        return self._traces.get(trace_id)

    def get_by_run_id(self, run_id: str) -> List[Dict[str, Any]]:
        return [
            trace
            for trace in self._traces.values()
            if trace["run_id"] == run_id
        ]

    def all(self) -> List[Dict[str, Any]]:
        return list(self._traces.values())

    def clear(self) -> None:
        self._traces.clear()

    # ==================================================
    # Debug / Observability
    # ==================================================

    def count(self) -> int:
        return len(self._traces)
