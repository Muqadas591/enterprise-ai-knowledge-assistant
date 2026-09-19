from pathlib import Path

import pymupdf

from app.rag.loaders.base import (
    DocumentLoader,
    ExtractedDocument,
    ExtractedPage,
)
from app.utils.text_utils import clean_text


class PDFLoader(DocumentLoader):
    def load(self, file_path: Path) -> ExtractedDocument:
        with pymupdf.open(file_path) as document:
            pages = [
                ExtractedPage(
                    page_number=page_index + 1,
                    text=clean_text(page.get_text()),
                )
                for page_index, page in enumerate(document)
            ]

        return ExtractedDocument(
            pages=pages,
            metadata={
                "format": "pdf",
                "page_count": len(pages),
            },
        )
