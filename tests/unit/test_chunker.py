import pytest

from app.rag.chunking.text_chunker import TextChunker


def test_chunker_creates_multiple_chunks() -> None:

    text = " ".join(f"word{i}" for i in range(1000))

    chunker = TextChunker(
        chunk_size=100,
        chunk_overlap=20,
    )

    chunks = chunker.chunk_text(text)

    assert len(chunks) > 1

    assert chunks[0].chunk_index == 0
    assert chunks[1].chunk_index == 1


def test_chunker_rejects_invalid_overlap() -> None:

    with pytest.raises(ValueError):
        TextChunker(
            chunk_size=100,
            chunk_overlap=100,
        )
