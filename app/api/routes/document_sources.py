from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.document_source import (
    DocumentSourceResponse,
)
from app.services.document_source_service import (
    DocumentSourceService,
)

router = APIRouter(
    prefix="/documents",
    tags=["Document Sources"],
)


@router.get(
    "/{document_id}/chunks/{chunk_index}",
    response_model=DocumentSourceResponse,
)
def get_document_source(
    document_id: int,
    chunk_index: int,
    db: Session = Depends(get_db),
):
    service = DocumentSourceService(db)

    source = service.get_source(
        document_id=document_id,
        chunk_index=chunk_index,
    )

    if source is None:
        raise HTTPException(
            status_code=404,
            detail="Document source not found.",
        )

    return source