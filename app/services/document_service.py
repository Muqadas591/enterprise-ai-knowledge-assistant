import json
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.services.ingestion_service import IngestionService


class DocumentService:
    def __init__(self, db: Session):
        self.db = db
        self.ingestion_service = IngestionService()

    def find_by_checksum(
        self,
        checksum: str,
    ) -> Document | None:

        statement = select(Document).where(Document.checksum == checksum)

        return self.db.execute(statement).scalar_one_or_none()

    def process_document(
        self,
        document: Document,
        file_path: Path,
    ) -> Document:

        document.status = "processing"

        self.db.add(document)
        self.db.commit()

        try:
            extracted = self.ingestion_service.extract(file_path)

            document.status = "processed"

            document.page_count = extracted.metadata.get("page_count")

            document.document_metadata = json.dumps(
                extracted.metadata,
                ensure_ascii=False,
            )

            document.error_message = None

            self.db.add(document)
            self.db.commit()
            self.db.refresh(document)

            return document

        except Exception as exc:
            document.status = "failed"
            document.error_message = str(exc)

            self.db.add(document)
            self.db.commit()

            raise
