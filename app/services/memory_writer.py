"""
Memory Writer

Responsible for persisting execution results into ExecutionHistoryRepository.

Acts as the persistence bridge between runtime execution and storage.

This layer is intentionally isolated to allow future support for:
- databases
- vector stores
- observability platforms
- audit logs
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from uuid import uuid4

from app.schemas.execution import ExecutionResult
from app.schemas.agent_execution_context import AgentExecutionContext
from app.schemas.execution_context import ExecutionContext
from app.repositories.execution_history_repository import ExecutionHistoryRepository

logger = logging.getLogger(__name__)


"""
Persists execution history records.

This is the ONLY component responsible for writing execution memory.
"""
class MemoryWriter:
    def __init__(
        self,
        history_repository: ExecutionHistoryRepository,
    ) -> None:
        self._history_repository = history_repository

    # ==================================================
    # Public API
    # ==================================================

    def write(
        self,
        execution_result: ExecutionResult,
        agent_context: AgentExecutionContext,
        session_context: Optional[ExecutionContext] = None,
    ) -> None:
        """
        Persist execution result and metadata.
        """
        now = datetime.now(timezone.utc)

        record: Dict[str, Any] = {
            "id": str(uuid4()),
            "execution_id": execution_result.execution_id,
            "status": execution_result.status,
            "output": execution_result.output,
            "error": execution_result.error,
            "child_results": [
                child.model_dump()
                for child in (execution_result.child_results or [])
            ],
            "metadata": {
                "task_id": session_context.task_id if session_context else None,
                "run_id": agent_context.run_id,
                "status": agent_context.status,
                "strategy": (
                    session_context.strategy.value
                    if session_context and hasattr(session_context, "strategy")
                    else None
                ),
            },
            "timestamps": {
                "created_at": now.isoformat(),
                "completed_at": now.isoformat(),
            },
            "session_context": (
                session_context.model_dump()
                if session_context is not None
                else None
            ),
        }

        self._history_repository.save(record)

        # Debug-level observability (safe for production)
        logger.debug("Stored execution record", extra={"execution_id": record["id"]})
