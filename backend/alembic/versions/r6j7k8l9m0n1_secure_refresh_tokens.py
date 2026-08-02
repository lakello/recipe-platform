"""secure refresh tokens

Revision ID: r6j7k8l9m0n1
Revises: p4h5i6j7k8l9
Create Date: 2026-07-26 19:30:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "r6j7k8l9m0n1"
down_revision: str | Sequence[str] | None = "p4h5i6j7k8l9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("DELETE FROM refresh_tokens")
    op.drop_index("ix_refresh_tokens_token", table_name="refresh_tokens")
    op.alter_column(
        "refresh_tokens",
        "token",
        new_column_name="token_hash",
        existing_type=sa.String(36),
        type_=sa.String(64),
        existing_nullable=False,
    )
    op.create_index(
        "ix_refresh_tokens_token_hash",
        "refresh_tokens",
        ["token_hash"],
        unique=True,
    )
    op.add_column(
        "refresh_tokens", sa.Column("family_id", sa.UUID(), nullable=False)
    )
    op.create_index(
        "ix_refresh_tokens_family_id",
        "refresh_tokens",
        ["family_id"],
        unique=False,
    )


def downgrade() -> None:
    op.execute("DELETE FROM refresh_tokens")
    op.drop_index("ix_refresh_tokens_family_id", table_name="refresh_tokens")
    op.drop_column("refresh_tokens", "family_id")
    op.drop_index("ix_refresh_tokens_token_hash", table_name="refresh_tokens")
    op.alter_column(
        "refresh_tokens",
        "token_hash",
        new_column_name="token",
        existing_type=sa.String(64),
        type_=sa.String(36),
        existing_nullable=False,
    )
    op.create_index(
        "ix_refresh_tokens_token",
        "refresh_tokens",
        ["token"],
        unique=True,
    )
