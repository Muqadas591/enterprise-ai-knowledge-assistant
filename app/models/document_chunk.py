from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import relationship

from app.core.config import settings
from app.core.database import Base


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, index=True)

    document_id = Column(
        Integer,
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    chunk_index = Column(
        Integer,
        nullable=False,
    )

    content = Column(
        Text,
        nullable=False,
    )

    page_number = Column(
        Integer,
        nullable=True,
    )

    section_title = Column(
        String(255),
        nullable=True,
    )

    token_count = Column(
        Integer,
        nullable=False,
    )

    embedding = Column(
        Vector(settings.EMBEDDING_DIMENSION),
        nullable=True,
    )

    search_vector = Column(
        TSVECTOR,
        nullable=True,
    )

    document = relationship(
        "Document",
        back_populates="chunks",
    )
