"""
RAG API router.

Provides endpoints to:
- ingest documents
- query knowledge base
"""

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel

from app.services.rag.rag_service import RAGService
from app.api.deps import get_rag_service


router = APIRouter(prefix="/rag", tags=["RAG"])


# =========================
# Schemas
# =========================

class DocumentIngest(BaseModel):
    document_id: str
    text: str


class QueryRequest(BaseModel):
    query: str
    k: int = 3


# =========================
# Endpoints
# =========================

@router.post(
    "/documents",
    status_code=status.HTTP_201_CREATED,
)
def ingest_document(
    doc: DocumentIngest,
    rag: RAGService = Depends(get_rag_service),
):
    rag.ingest(
        document_id=doc.document_id,
        text=doc.text,
    )

    return {"status": "ingested", "document_id": doc.document_id}


@router.post("/query")
def query(
    request: QueryRequest,
    rag: RAGService = Depends(get_rag_service),
):
    results = rag.query(
        query=request.query,
        k=request.k,
    )

    return {
        "query": request.query,
        "results": results,
    }