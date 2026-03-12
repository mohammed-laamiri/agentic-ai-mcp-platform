"""
Execution History Repository

Stores execution records for tasks, agents, and tools.

Supports:
- In-memory storage for tests or ephemeral tracking
- Extendable to persistent databases
"""

from typing import List, Dict, Optional
from threading import Lock
import uuid


class ExecutionHistoryRepository:
    """
    Simple thread-safe in-memory execution history repository.
    """

    def __init__(self):
        self._records: List[Dict] = []
        self._lock = Lock()

    def save(self, record: Dict) -> None:
        """
        Save a new execution record.
        Automatically generates a unique ID if not provided.
        """
        with self._lock:
            if "id" not in record:
                record["id"] = str(uuid.uuid4())
            self._records.append(record)

    def all(self) -> List[Dict]:
        """
        Return all execution records.
        """
        with self._lock:
            return list(self._records)

    def find_by_task_id(self, task_id: str) -> List[Dict]:
        """
        Find all records for a given task ID.
        """
        with self._lock:
            return [r for r in self._records if r.get("metadata", {}).get("task_id") == task_id]

    def clear(self) -> None:
        """
        Clear all stored records (useful for tests).
        """
        with self._lock:
            self._records.clear()
