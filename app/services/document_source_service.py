from sqlalchemy.orm import Session

from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.schemas.document_source import DocumentSourceResponse


class DocumentSourceService:
    def __init__(self, db: Session) -> None:
        self.chunk_repository = DocumentChunkRepository(db)

    def get_source(
        self,
        document_id: int,
        chunk_index: int,
    ) -> DocumentSourceResponse | None:
        chunk = self.chunk_repository.get_chunk_by_document_and_index(
            document_id=document_id,
            chunk_index=chunk_index,
        )

        if chunk is None:
            return None

        return DocumentSourceResponse(
            document_id=str(chunk.document_id),
            filename=chunk.document.filename,
            chunk_index=chunk.chunk_index,
            page_number=chunk.page_number,
            section_title=chunk.section_title,
            content=chunk.content,
        )