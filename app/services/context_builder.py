from dataclasses import dataclass

from app.schemas.retrieval import RetrievalResult


@dataclass
class ContextSource:
    source_id: str
    document_id: int
    filename: str
    chunk_id: int
    chunk_index: int
    page_number: int | None
    content: str


class ContextBuilder:
    def build(
        self,
        results: list[RetrievalResult],
    ) -> tuple[str, list[ContextSource]]:
        sources: list[ContextSource] = []
        context_blocks: list[str] = []

        for index, result in enumerate(results, start=1):
            source_id = f"S{index}"
            filename = result.filename or "unknown"

            source = ContextSource(
                source_id=source_id,
                document_id=result.document_id,
                filename=filename,
                chunk_id=result.chunk_id,
                chunk_index=result.chunk_index,
                page_number=result.page_number,
                content=result.content,
            )
            sources.append(source)

            page_text = str(result.page_number) if result.page_number is not None else "N/A"
            context_blocks.append(
                f"[{source_id}]\n"
                f"Document: {filename}\n"
                f"Document ID: {result.document_id}\n"
                f"Chunk ID: {result.chunk_id}\n"
                f"Chunk Index: {result.chunk_index}\n"
                f"Page: {page_text}\n"
                f"Content:\n{result.content}\n"
            )

        return "\n\n".join(context_blocks), sources
