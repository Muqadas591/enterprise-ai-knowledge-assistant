from app.rag.embeddings.factory import get_embedding_service
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.schemas.retrieval_filters import RetrievalFilters


class RetrievalService:
    """Semantic retrieval service for RAG."""

    def __init__(self, db):
        self.repository = DocumentChunkRepository(db)
        self.embedding_service = get_embedding_service()

    def search(
        self,
        query: str,
        top_k: int = 5,
        filters: RetrievalFilters | None = None,
    ):
        if not query.strip():
            raise ValueError("Query cannot be empty.")

        query_embedding = self.embedding_service.embed_query(query)

        return self.repository.similarity_search(
            query_embedding=query_embedding,
            top_k=top_k,
            filters=filters,
        )
