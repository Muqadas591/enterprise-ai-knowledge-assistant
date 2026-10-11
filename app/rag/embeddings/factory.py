from app.rag.embeddings.service import (
    EmbeddingService,
    LocalEmbeddingService,
)


def get_embedding_service() -> EmbeddingService:
    """
    Return the configured embedding provider.
    """

    return LocalEmbeddingService()
