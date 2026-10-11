"""add document chunk full text search

Revision ID: 10ee106546c9
Revises: b53ceb7f305f
Create Date: 2026-09-20 19:16:17.512716

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '10ee106546c9'
down_revision: Union[str, Sequence[str], None] = 'b53ceb7f305f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        ALTER TABLE document_chunks
        ADD COLUMN IF NOT EXISTS search_vector tsvector
        """
    )

    op.execute(
        """
        CREATE OR REPLACE FUNCTION document_chunks_search_vector_update()
        RETURNS trigger AS $$
        BEGIN
            NEW.search_vector := to_tsvector(
                'english',
                COALESCE(NEW.content, '')
            );
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql
        """
    )

    op.execute(
        """
        DROP TRIGGER IF EXISTS document_chunks_search_vector_trigger
        ON document_chunks
        """
    )

    op.execute(
        """
        CREATE TRIGGER document_chunks_search_vector_trigger
        BEFORE INSERT OR UPDATE OF content
        ON document_chunks
        FOR EACH ROW
        EXECUTE FUNCTION document_chunks_search_vector_update()
        """
    )

    op.execute(
        """
        UPDATE document_chunks
        SET search_vector = to_tsvector(
            'english',
            COALESCE(content, '')
        )
        """
    )

    op.execute(
        """
        CREATE INDEX IF NOT EXISTS document_chunks_search_vector_idx
        ON document_chunks
        USING gin(search_vector)
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        DROP TRIGGER IF EXISTS document_chunks_search_vector_trigger
        ON document_chunks
        """
    )

    op.execute(
        """
        DROP FUNCTION IF EXISTS document_chunks_search_vector_update()
        """
    )

    op.execute(
        """
        DROP INDEX IF EXISTS document_chunks_search_vector_idx
        """
    )

    op.execute(
        """
        ALTER TABLE document_chunks
        DROP COLUMN IF EXISTS search_vector
        """
    )
