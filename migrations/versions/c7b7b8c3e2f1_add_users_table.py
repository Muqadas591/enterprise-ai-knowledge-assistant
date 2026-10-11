"""add user full name

Revision ID: c7b7b8c3e2f1
Revises: b53ceb7f305f
Create Date: 2026-09-21

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "c7b7b8c3e2f1"
down_revision: str | Sequence[str] | None = "10ee106546c9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("full_name", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "full_name")
