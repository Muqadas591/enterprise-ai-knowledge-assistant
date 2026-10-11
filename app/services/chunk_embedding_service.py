from app.core.config import settings
from app.models.document_chunk import DocumentChunk
from app.rag.chunking.text_chunker import TokenTextChunker
from app.rag.embeddings.factory import get_embedding_service


class ChunkEmbeddingService:
    """Convert extracted document pages into database-ready chunks with embeddings."""

    def __init__(self) -> None:
        self.chunker = TokenTextChunker()
        self.embedding_service = get_embedding_service()

    def create_chunks(
        self,
        pages,
        document_id: int,
    ) -> list[DocumentChunk]:
        chunks = self.chunker.chunk_pages(pages)

        if not chunks:
            return []

        embeddings = self.embedding_service.embed_documents([chunk.content for chunk in chunks])

        if len(chunks) != len(embeddings):
            raise RuntimeError("Chunk count does not match embedding count.")

        database_chunks = []

        for chunk, embedding in zip(chunks, embeddings):
            if len(embedding) != settings.EMBEDDING_DIMENSION:
                raise RuntimeError(
                    "Embedding dimension does not match the configured embedding dimension."
                )

            database_chunks.append(
                DocumentChunk(
                    document_id=document_id,
                    chunk_index=chunk.chunk_index,
                    content=chunk.content,
                    page_number=chunk.page_number,
                    section_title=chunk.section_title,
                    token_count=chunk.token_count,
                    embedding=embedding,
                )
            )

        return database_chunks
