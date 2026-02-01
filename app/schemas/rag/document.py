from pydantic import BaseModel
from typing import Dict, Any
from uuid import uuid4


class Document(BaseModel):
    """
    Raw ingested document.
    """
    id: str = str(uuid4())
    content: str
    metadata: Dict[str, Any] = {}
