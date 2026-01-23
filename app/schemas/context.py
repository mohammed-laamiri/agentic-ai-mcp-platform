from pydantic import BaseModel
from typing import Any


class ExecutionContext(BaseModel):
    """
    Shared context passed between agents and tools.
    """

    session_id: str
    user_id: str | None = None
    metadata: dict[str, Any] = {}
