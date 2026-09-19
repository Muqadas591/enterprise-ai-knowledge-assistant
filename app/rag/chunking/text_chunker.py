from dataclasses import dataclass


@dataclass
class TextChunk:
    content: str
    chunk_index: int
    page_number: int | None


class TextChunker:
    def __init__(
        self,
        chunk_size: int = 800,
        chunk_overlap: int = 120,
    ):
        if chunk_overlap >= chunk_size:
            raise ValueError("Chunk overlap must be smaller than chunk size.")

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_text(
        self,
        text: str,
        page_number: int | None = None,
    ) -> list[TextChunk]:

        words = text.split()

        chunks: list[TextChunk] = []

        start = 0
        chunk_index = 0

        while start < len(words):
            end = min(
                start + self.chunk_size,
                len(words),
            )

            content = " ".join(words[start:end]).strip()

            if content:
                chunks.append(
                    TextChunk(
                        content=content,
                        chunk_index=chunk_index,
                        page_number=page_number,
                    )
                )

                chunk_index += 1

            if end >= len(words):
                break

            start = end - self.chunk_overlap

        return chunks
