from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.document import Document
from app.models.document_chunk import DocumentChunk
from app.schemas.retrieval_filters import RetrievalFilters


class DocumentChunkRepository:
    """Database operations for document chunks."""

    def __init__(self, db: Session):
        self.db = db

    def add_chunks(
        self,
        chunks: list[DocumentChunk],
    ) -> None:
        self.db.add_all(chunks)

    def get_chunk_by_document_and_index(
        self,
        document_id: int,
        chunk_index: int,
    ) -> DocumentChunk | None:
        statement = select(DocumentChunk).where(
            DocumentChunk.document_id == document_id,
            DocumentChunk.chunk_index == chunk_index,
        )

        return self.db.execute(statement).scalar_one_or_none()

    @staticmethod
    def _apply_filters(statement, filters: RetrievalFilters | None):
        if not filters:
            return statement

        if filters.document_id is not None:
            statement = statement.where(Document.id == filters.document_id)

        if filters.document_category:
            statement = statement.where(Document.document_category == filters.document_category)

        if filters.document_type:
            statement = statement.where(Document.document_type == filters.document_type)

        if filters.department:
            statement = statement.where(Document.department == filters.department)

        return statement

    def similarity_search(
        self,
        query_embedding: list[float],
        top_k: int = 5,
        filters: RetrievalFilters | None = None,
    ):
        distance = DocumentChunk.embedding.cosine_distance(query_embedding)

        statement = (
            select(
                DocumentChunk,
                Document,
                (1 - distance).label("similarity"),
            )
            .join(
                Document,
                Document.id == DocumentChunk.document_id,
            )
            .where(DocumentChunk.embedding.is_not(None))
        )

        statement = self._apply_filters(statement, filters)

        statement = statement.order_by(distance).limit(top_k)

        return self.db.execute(statement).all()

    def keyword_search(
        self,
        query: str,
        top_k: int = 5,
        filters: RetrievalFilters | None = None,
    ):
        ts_query = func.websearch_to_tsquery("english", query)
        rank = func.ts_rank_cd(
            DocumentChunk.search_vector,
            ts_query,
        )

        statement = (
            select(
                DocumentChunk,
                Document,
                rank.label("keyword_score"),
            )
            .join(
                Document,
                Document.id == DocumentChunk.document_id,
            )
            .where(DocumentChunk.search_vector.op("@@")(ts_query))
        )

        statement = self._apply_filters(statement, filters)

        statement = statement.order_by(rank.desc()).limit(top_k)

        return self.db.execute(statement).all()
