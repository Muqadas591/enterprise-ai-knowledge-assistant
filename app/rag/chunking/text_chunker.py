from dataclasses import dataclass

import tiktoken

from app.core.config import settings


@dataclass
class TextChunk:
    content: str
    chunk_index: int
    token_count: int
    page_number: int | None = None
    section_title: str | None = None


class TokenTextChunker:
    """
    Token-aware text chunker for RAG pipelines.

    Chunks are created according to tokenizer token counts rather
    than approximate word counts.
    """

    def __init__(
        self,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
    ):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

        if self.chunk_overlap >= self.chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size")

        self.tokenizer = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text: str) -> int:
        """Return the number of tokens in text."""
        return len(self.tokenizer.encode(text))

    def split_text(self, text: str) -> list[str]:
        """
        Split text into overlapping token-based chunks.
        """

        if not text or not text.strip():
            return []

        tokens = self.tokenizer.encode(text)

        chunks = []

        start = 0

        while start < len(tokens):
            end = min(start + self.chunk_size, len(tokens))

            chunk_tokens = tokens[start:end]
            chunk_text = self.tokenizer.decode(chunk_tokens).strip()

            if chunk_text:
                chunks.append(chunk_text)

            if end >= len(tokens):
                break

            start = end - self.chunk_overlap

        return chunks

    def chunk_pages(self, pages) -> list[TextChunk]:
        """
        Create chunks while preserving page metadata.
        """

        chunks: list[TextChunk] = []

        chunk_index = 0

        for page in pages:
            page_chunks = self.split_text(page.text)

            for content in page_chunks:
                chunks.append(
                    TextChunk(
                        content=content,
                        chunk_index=chunk_index,
                        token_count=self.count_tokens(content),
                        page_number=page.page_number,
                        section_title=None,
                    )
                )

                chunk_index += 1

        return chunks
