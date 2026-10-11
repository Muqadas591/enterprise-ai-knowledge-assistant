import logging
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.api.deps import get_db
from app.core.config import settings
from app.models.document import Document
from app.models.user import User
from app.schemas.document import DocumentResponse
from app.services.document_service import DocumentService
from app.utils.file_utils import (
    calculate_sha256,
    generate_stored_filename,
    is_allowed_extension,
)

router = APIRouter(
    prefix="/documents",
    tags=["Documents"],
)

logger = logging.getLogger(__name__)


@router.get(
    "",
    response_model=list[DocumentResponse],
)
def list_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[Document]:

    statement = select(Document).order_by(Document.created_at.desc())

    return list(db.execute(statement).scalars().all())


@router.post(
    "/upload",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFile = File(...),
    document_category: str | None = Form(default=None),
    document_type: str | None = Form(default=None),
    department: str | None = Form(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Document:

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    if not is_allowed_extension(
        file.filename,
        settings.ALLOWED_FILE_EXTENSIONS,
    ):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type.",
        )

    content = await file.read()

    max_size = settings.MAX_FILE_SIZE_MB * 1024 * 1024

    if len(content) > max_size:
        raise HTTPException(
            status_code=413,
            detail=(f"File exceeds the maximum size of {settings.MAX_FILE_SIZE_MB} MB."),
        )

    upload_directory = Path(settings.UPLOAD_DIRECTORY)

    upload_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    stored_filename = generate_stored_filename(file.filename)

    file_path = upload_directory / stored_filename

    file_path.write_bytes(content)

    checksum = calculate_sha256(file_path)

    service = DocumentService(db)

    existing = service.find_by_checksum(checksum)

    if existing:
        file_path.unlink(missing_ok=True)

        raise HTTPException(
            status_code=409,
            detail=("This document has already been uploaded."),
        )

    document = Document(
        filename=file.filename,
        stored_filename=stored_filename,
        file_type=Path(file.filename).suffix.lower(),
        file_size=len(content),
        checksum=checksum,
        status="uploaded",
        document_category=document_category,
        document_type=document_type,
        department=department,
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    try:
        service.process_document(
            document,
            file_path,
        )

    except Exception as exc:
        logger.exception("Document processing failed for document %s", document.id)
        raise HTTPException(
            status_code=500,
            detail="Document processing failed.",
        ) from exc

    return document


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Document:

    document = db.get(
        Document,
        document_id,
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    return document


@router.delete(
    "/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Response:
    document = db.get(Document, document_id)

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found.",
        )

    file_path = Path(settings.UPLOAD_DIRECTORY) / document.stored_filename

    db.delete(document)
    db.commit()

    try:
        file_path.unlink(missing_ok=True)
    except OSError:
        logger.exception("Unable to remove stored file for document %s", document_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
