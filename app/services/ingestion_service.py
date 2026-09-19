import json
from pathlib import Path

from app.core.config import settings
from app.rag.chunking.text_chunker import TextChunker
from app.rag.loaders import get_loader
from app.rag.loaders.base import ExtractedDocument


class IngestionService:
    def __init__(self) -> None:
        self.chunker = TextChunker(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
        )

    def extract(
        self,
        file_path: Path,
    ) -> ExtractedDocument:

        loader = get_loader(file_path)

        return loader.load(file_path)

    def serialize_metadata(
        self,
        metadata: dict,
    ) -> str:

        return json.dumps(
            metadata,
            ensure_ascii=False,
        )
