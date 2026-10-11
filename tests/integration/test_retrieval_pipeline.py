from collections.abc import Generator
from uuid import uuid4

import pytest
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.repositories.document_chunk_repository import DocumentChunkRepository
from app.schemas.retrieval_filters import RetrievalFilters
from app.services.hybrid_retrieval_service import HybridRetrievalService


@pytest.fixture
def db() -> Generator[Session, None, None]:
    session = SessionLocal()

    try:
        session.connection()
    except SQLAlchemyError as exc:
        session.close()
        pytest.skip(f"PostgreSQL integration database unavailable: {exc}")

    try:
        yield session
    finally:
        session.rollback()
        session.close()


def vector(first_value: float) -> list[float]:
    return [first_value] + [0.0] * 383


def create_synthetic_documents(session: Session) -> tuple[Document, Document]:
    suffix = uuid4().hex
    hr_document = Document(
        filename=f"integration_hr_{suffix}.txt",
        stored_filename=f"stored_hr_{suffix}.txt",
        file_type=".txt",
        file_size=10,
        checksum=uuid4().hex + uuid4().hex,
        status="processed",
        document_category="HR",
        document_type="policy",
        department="HR",
    )
    it_document = Document(
        filename=f"integration_it_{suffix}.txt",
        stored_filename=f"stored_it_{suffix}.txt",
        file_type=".txt",
        file_size=10,
        checksum=uuid4().hex + uuid4().hex,
        status="processed",
        document_category="IT",
        document_type="policy",
        department="IT",
    )
    session.add_all([hr_document, it_document])
    session.flush()

    session.add_all(
        [
            DocumentChunk(
                document_id=hr_document.id,
                chunk_index=0,
                content="Annual leave policy for permanent employees.",
                token_count=7,
                embedding=vector(1.0),
            ),
            DocumentChunk(
                document_id=it_document.id,
                chunk_index=0,
                content="VPN-ACCESS-17 is required for remote access.",
                token_count=8,
                embedding=vector(0.9),
            ),
        ]
    )
    session.flush()

    return hr_document, it_document


def test_vector_metadata_keyword_and_hybrid_retrieval(db: Session):
    hr_document, it_document = create_synthetic_documents(db)
    repository = DocumentChunkRepository(db)

    vector_results = repository.similarity_search(
        query_embedding=vector(1.0),
        top_k=5,
        filters=RetrievalFilters(document_category="HR"),
    )
    assert vector_results
    assert all(document.id == hr_document.id for chunk, document, score in vector_results)

    keyword_results = repository.keyword_search(
        query="VPN-ACCESS-17",
        top_k=5,
    )
    assert keyword_results
    assert keyword_results[0][1].id == it_document.id

    hybrid_service = HybridRetrievalService.__new__(HybridRetrievalService)
    hybrid_service.repository = repository
    hybrid_service.embedding_service = type(
        "FakeEmbeddingService",
        (),
        {"embed_query": lambda self, query: vector(1.0)},
    )()

    hybrid_results = hybrid_service.search(
        query="VPN-ACCESS-17",
        top_k=2,
    )
    assert hybrid_results
    assert hybrid_results[0][1].id == it_document.id
