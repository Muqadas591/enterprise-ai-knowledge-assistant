from dataclasses import dataclass

from app.core.config import settings


@dataclass(frozen=True)
class EmbeddingConfig:
    model_name: str
    dimension: int
    normalize_embeddings: bool


DEFAULT_EMBEDDING_CONFIG = EmbeddingConfig(
    model_name=settings.EMBEDDING_MODEL,
    dimension=settings.EMBEDDING_DIMENSION,
    normalize_embeddings=settings.EMBEDDING_NORMALIZE,
)
