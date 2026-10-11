from app.rag.embeddings.factory import get_embedding_service
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.schemas.retrieval_filters import RetrievalFilters
from app.services.ranking_service import reciprocal_rank_fusion


class HybridRetrievalService:
    """Combine semantic and keyword retrieval using reciprocal rank fusion."""

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
        vector_results = self.repository.similarity_search(
            query_embedding=query_embedding,
            top_k=top_k * 2,
            filters=filters,
        )
        keyword_results = self.repository.keyword_search(
            query=query,
            top_k=top_k * 2,
            filters=filters,
        )

        vector_ids = [chunk.id for chunk, document, score in vector_results]
        keyword_ids = [chunk.id for chunk, document, score in keyword_results]
        fused = reciprocal_rank_fusion([vector_ids, keyword_ids])

        vector_lookup = {chunk.id: (chunk, document) for chunk, document, score in vector_results}
        keyword_lookup = {chunk.id: (chunk, document) for chunk, document, score in keyword_results}

        final_results = []
        for chunk_id, rrf_score in fused:
            if chunk_id in vector_lookup:
                chunk, document = vector_lookup[chunk_id]
            else:
                chunk, document = keyword_lookup[chunk_id]

            final_results.append((chunk, document, rrf_score))

            if len(final_results) >= top_k:
                break

        return final_results
