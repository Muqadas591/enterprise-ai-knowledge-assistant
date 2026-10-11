"""add hnsw vector index

Revision ID: 977355f9e977
Revises: 47dc889ac54c
Create Date: 2026-09-20 19:07:29.603810

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '977355f9e977'
down_revision: Union[str, Sequence[str], None] = '47dc889ac54c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        CREATE INDEX IF NOT EXISTS document_chunks_embedding_hnsw_idx
        ON document_chunks
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        DROP INDEX IF EXISTS document_chunks_embedding_hnsw_idx
        """
    )
