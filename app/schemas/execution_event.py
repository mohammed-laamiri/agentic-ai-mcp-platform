"""
Execution Event Schema

Represents structured streaming events emitted during execution.

Used by:
- ExecutionService (emits events)
- OrchestratorService (forwards events)
- API layer (formats SSE)
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


# ==========================================================
# Event Types
# ==========================================================

class ExecutionEventType(str, Enum):
    PLANNING_STARTED = "planning_started"
    PLAN_CREATED = "plan_created"
    EXECUTION_STARTED = "execution_started"
    PLAN_EXECUTION_STARTED = "plan_execution_started"
    STEP_STARTED = "step_started"
    TOKEN_CHUNK = "token_chunk" 
    STEP_COMPLETED = "step_completed"
    EXECUTION_COMPLETED = "execution_completed"
    EXECUTION_FAILED = "execution_failed"


# ==========================================================
# Base Execution Event
# ==========================================================

class ExecutionEvent(BaseModel):
    """
    Strongly-typed execution event.

    Fields:
    - type: Event type
    - step_index: Optional step index
    - strategy: Execution strategy (if applicable)
    - steps: Plan steps (if applicable)
    - result: Final execution result (if applicable)
    - error: Error message (if failed)
    - metadata: Flexible extension field
    """

    type: ExecutionEventType

    step_id: Optional[int] = None
    strategy: Optional[str] = None
    token: Optional[str] = None
    steps: Optional[List[Dict[str, Any]]] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None