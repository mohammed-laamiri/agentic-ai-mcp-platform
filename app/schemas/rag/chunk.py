from pydantic import BaseModel
from typing import Dict, Any


class DocumentChunk(BaseModel):
    """
    A chunked portion of a document.
    """
    chunk_id: str
    document_id: str
    content: str
    metadata: Dict[str, Any] = {}
