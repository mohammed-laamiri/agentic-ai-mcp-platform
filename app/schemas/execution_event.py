"""
Execution Event Schema

Represents structured streaming events emitted during execution.
Used for SSE streaming between ExecutionService → API → UI.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Union
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
# Execution Event
# ==========================================================

class ExecutionEvent(BaseModel):
    """
    SSE-safe execution event.
    Only primitives allowed (NO datetime, NO ORM objects).
    """

    type: ExecutionEventType

    # execution tracking (FIXED)
    execution_id: Optional[str] = None

    step_id: Optional[Union[str, int]] = None
    step_name: Optional[str] = None
    strategy: Optional[str] = None
    token: Optional[str] = None

    steps: Optional[List[Dict[str, Any]]] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    metadata: Optional[Dict[str, Any]] = None