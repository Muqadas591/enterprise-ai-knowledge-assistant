from pathlib import Path

from docx import Document

from app.rag.loaders.docx import DOCXLoader


def test_docx_loader(tmp_path: Path) -> None:

    file_path = tmp_path / "test.docx"

    document = Document()

    document.add_paragraph("Enterprise RAG test document.")

    document.save(file_path)

    loader = DOCXLoader()

    extracted = loader.load(file_path)

    assert len(extracted.pages) == 1

    assert "Enterprise RAG" in extracted.pages[0].text
