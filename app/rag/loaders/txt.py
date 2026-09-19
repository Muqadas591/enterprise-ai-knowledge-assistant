from pathlib import Path

from app.rag.loaders.base import (
    DocumentLoader,
    ExtractedDocument,
    ExtractedPage,
)
from app.utils.text_utils import clean_text


class TXTLoader(DocumentLoader):
    def load(
        self,
        file_path: Path,
    ) -> ExtractedDocument:

        full_text = clean_text(file_path.read_text(encoding="utf-8"))

        pages = [
            ExtractedPage(
                page_number=None,
                text=full_text,
            )
        ]

        metadata = {
            "format": "txt",
        }

        return ExtractedDocument(
            pages=pages,
            metadata=metadata,
        )
