from abc import ABC, abstractmethod

from app.rag.embeddings.config import (
    DEFAULT_EMBEDDING_CONFIG,
    EmbeddingConfig,
)


class EmbeddingService(ABC):
    """Abstract interface for embedding providers."""

    @abstractmethod
    def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        raise NotImplementedError

    @abstractmethod
    def embed_query(
        self,
        text: str,
    ) -> list[float]:
        raise NotImplementedError


class LocalEmbeddingService(EmbeddingService):
    """
    Sentence Transformer embedding implementation.

    The model is loaded only when this service is instantiated.
    """

    def __init__(
        self,
        config: EmbeddingConfig | None = None,
    ):
        self.config = config or DEFAULT_EMBEDDING_CONFIG

        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(self.config.model_name)

    def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        if not texts:
            return []

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=self.config.normalize_embeddings,
            convert_to_numpy=True,
            show_progress_bar=False,
        )

        return embeddings.tolist()

    def embed_query(
        self,
        text: str,
    ) -> list[float]:
        if not text.strip():
            raise ValueError("Query text cannot be empty.")

        embedding = self.model.encode(
            text,
            normalize_embeddings=self.config.normalize_embeddings,
            convert_to_numpy=True,
            show_progress_bar=False,
        )

        return embedding.tolist()
