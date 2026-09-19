from pathlib import Path

from app.rag.loaders.txt import TXTLoader


def test_txt_loader(tmp_path: Path) -> None:

    file_path = tmp_path / "test.txt"

    file_path.write_text(
        "Hello enterprise RAG.",
        encoding="utf-8",
    )

    loader = TXTLoader()

    document = loader.load(file_path)

    assert len(document.pages) == 1
    assert document.pages[0].text == "Hello enterprise RAG."
