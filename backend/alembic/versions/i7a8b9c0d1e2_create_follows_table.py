"""create follows table

Revision ID: i7a8b9c0d1e2
Revises: h6f7a8b9c1d2
Create Date: 2026-06-07 14:50:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "i7a8b9c0d1e2"
down_revision: str | None = "h6f7a8b9c1d2"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "follows",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("follower_id", sa.UUID(), nullable=False),
        sa.Column("following_id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["follower_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["following_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("follower_id", "following_id", name="uq_follow"),
    )
    op.create_index(
        op.f("ix_follows_follower_id"), "follows", ["follower_id"], unique=False
    )
    op.create_index(
        op.f("ix_follows_following_id"), "follows", ["following_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_follows_following_id"), table_name="follows")
    op.drop_index(op.f("ix_follows_follower_id"), table_name="follows")
    op.drop_table("follows")
