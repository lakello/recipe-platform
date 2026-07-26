"""add upload intents

Revision ID: s8k9l0m1n2o3
Revises: r6j7k8l9m0n1
Create Date: 2026-07-26 20:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "s8k9l0m1n2o3"
down_revision: str | Sequence[str] | None = "r6j7k8l9m0n1"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "upload_intents",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("recipe_id", sa.UUID(), nullable=True),
        sa.Column("upload_type", sa.String(20), nullable=False),
        sa.Column("bucket", sa.String(255), nullable=False),
        sa.Column("object_key", sa.String(512), nullable=False),
        sa.Column("expected_content_type", sa.String(50), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["recipe_id"], ["recipes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("object_key"),
    )
    op.create_index(
        "ix_upload_intents_expires_at",
        "upload_intents",
        ["expires_at"],
    )
    op.create_index(
        "ix_upload_intents_status", "upload_intents", ["status"]
    )
    op.create_index(
        "ix_upload_intents_user_id", "upload_intents", ["user_id"]
    )


def downgrade() -> None:
    op.drop_index("ix_upload_intents_user_id", table_name="upload_intents")
    op.drop_index("ix_upload_intents_status", table_name="upload_intents")
    op.drop_index("ix_upload_intents_expires_at", table_name="upload_intents")
    op.drop_table("upload_intents")
