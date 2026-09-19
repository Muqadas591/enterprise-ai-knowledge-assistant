from pathlib import Path

from app.rag.loaders.base import DocumentLoader
from app.rag.loaders.docx import DOCXLoader
from app.rag.loaders.pdf import PDFLoader
from app.rag.loaders.txt import TXTLoader


def get_loader(
    file_path: Path,
) -> DocumentLoader:

    extension = file_path.suffix.lower()

    loaders = {
        ".pdf": PDFLoader,
        ".docx": DOCXLoader,
        ".txt": TXTLoader,
    }

    loader_class = loaders.get(extension)

    if loader_class is None:
        raise ValueError(f"Unsupported file extension: {extension}")

    return loader_class()
