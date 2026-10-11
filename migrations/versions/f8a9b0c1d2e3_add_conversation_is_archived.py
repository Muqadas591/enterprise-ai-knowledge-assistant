"""add conversation is_archived

Revision ID: f8a9b0c1d2e3
Revises: 6ef903b6eb78
Create Date: 2026-10-07

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "f8a9b0c1d2e3"
down_revision: str | Sequence[str] | None = "6ef903b6eb78"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "conversations",
        sa.Column(
            "is_archived",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
    )
    op.create_index(
        op.f("ix_conversations_is_archived"),
        "conversations",
        ["is_archived"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_conversations_is_archived"), table_name="conversations")
    op.drop_column("conversations", "is_archived")
