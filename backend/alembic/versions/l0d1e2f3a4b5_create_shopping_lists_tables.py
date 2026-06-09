"""create shopping lists tables

Revision ID: l0d1e2f3a4b5
Revises: k9c0d1e2f3a4
Create Date: 2026-06-08 14:30:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from alembic import op

revision: str = "l0d1e2f3a4b5"
down_revision: str | None = "k9c0d1e2f3a4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "shopping_lists",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("last_generated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_shopping_list_user"),
    )
    op.create_index("ix_shopping_lists_user_id", "shopping_lists", ["user_id"])

    op.create_table(
        "shopping_list_items",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("shopping_list_id", UUID(as_uuid=True), nullable=False),
        sa.Column("ingredient_id", UUID(as_uuid=True), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("amount", sa.Numeric(10, 3), nullable=True),
        sa.Column("unit", sa.String(20), nullable=True),
        sa.Column("is_bought", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("is_manual", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["shopping_list_id"], ["shopping_lists.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["ingredient_id"], ["ingredients.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_shopping_list_items_list_id", "shopping_list_items", ["shopping_list_id"]
    )
    op.create_index(
        "ix_shopping_list_items_ingredient_id",
        "shopping_list_items",
        ["ingredient_id"],
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("shopping_list_items")
    op.drop_table("shopping_lists")
