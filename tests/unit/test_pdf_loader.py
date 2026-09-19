from pathlib import Path

import fitz

from app.rag.loaders.pdf import PDFLoader


def test_pdf_loader(tmp_path: Path) -> None:

    file_path = tmp_path / "test.pdf"

    document = fitz.open()

    page = document.new_page()

    page.insert_text(
        (72, 72),
        "Enterprise RAG test document.",
    )

    document.save(file_path)
    document.close()

    loader = PDFLoader()

    extracted = loader.load(file_path)

    assert len(extracted.pages) == 1

    assert "Enterprise RAG" in extracted.pages[0].text
