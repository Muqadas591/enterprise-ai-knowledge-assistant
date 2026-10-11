from app.rag.chunking.text_chunker import TokenTextChunker


def test_token_chunker_returns_chunks():
    chunker = TokenTextChunker(
        chunk_size=50,
        chunk_overlap=10,
    )

    text = "This is a test sentence. " * 100

    chunks = chunker.split_text(text)

    assert len(chunks) > 1
    assert all(chunk.strip() for chunk in chunks)


def test_token_count():
    chunker = TokenTextChunker(
        chunk_size=100,
        chunk_overlap=20,
    )

    text = "This is a simple test."

    token_count = chunker.count_tokens(text)

    assert token_count > 0


def test_invalid_overlap():
    try:
        TokenTextChunker(
            chunk_size=50,
            chunk_overlap=50,
        )
        assert False
    except ValueError:
        assert True
