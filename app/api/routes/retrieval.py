from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.api.deps import get_db
from app.models.user import User
from app.schemas.retrieval import RetrievalResponse, RetrievalResult
from app.schemas.retrieval_filters import RetrievalFilters
from app.services.hybrid_retrieval_service import HybridRetrievalService
from app.services.retrieval_service import RetrievalService

router = APIRouter(
    prefix="/api/v1/retrieval",
    tags=["retrieval"],
)


@router.get(
    "/search",
    response_model=RetrievalResponse,
)
def search_documents(
    query: str = Query(..., min_length=2),
    top_k: int = Query(default=5, ge=1, le=20),
    document_category: str | None = Query(default=None),
    document_type: str | None = Query(default=None),
    department: str | None = Query(default=None),
    document_id: int | None = Query(default=None, ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = RetrievalFilters(
        document_category=document_category,
        document_type=document_type,
        department=department,
        document_id=document_id,
    )

    results = RetrievalService(db).search(
        query=query,
        top_k=top_k,
        filters=filters,
    )

    formatted_results = [
        RetrievalResult(
            chunk_id=chunk.id,
            document_id=chunk.document_id,
            chunk_index=chunk.chunk_index,
            content=chunk.content,
            page_number=chunk.page_number,
            section_title=chunk.section_title,
            score=float(score),
            filename=document.filename,
            document_category=document.document_category,
            document_type=document.document_type,
            department=document.department,
        )
        for chunk, document, score in results
    ]

    return RetrievalResponse(
        query=query,
        results=formatted_results,
    )


@router.get(
    "/hybrid-search",
    response_model=RetrievalResponse,
)
def hybrid_search_documents(
    query: str = Query(..., min_length=2),
    top_k: int = Query(default=5, ge=1, le=20),
    document_category: str | None = Query(default=None),
    document_type: str | None = Query(default=None),
    department: str | None = Query(default=None),
    document_id: int | None = Query(default=None, ge=1),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    filters = RetrievalFilters(
        document_category=document_category,
        document_type=document_type,
        department=department,
        document_id=document_id,
    )

    results = HybridRetrievalService(db).search(
        query=query,
        top_k=top_k,
        filters=filters,
    )

    formatted_results = [
        RetrievalResult(
            chunk_id=chunk.id,
            document_id=chunk.document_id,
            chunk_index=chunk.chunk_index,
            content=chunk.content,
            page_number=chunk.page_number,
            section_title=chunk.section_title,
            score=float(score),
            filename=document.filename,
            document_category=document.document_category,
            document_type=document.document_type,
            department=document.department,
        )
        for chunk, document, score in results
    ]

    return RetrievalResponse(
        query=query,
        results=formatted_results,
    )
