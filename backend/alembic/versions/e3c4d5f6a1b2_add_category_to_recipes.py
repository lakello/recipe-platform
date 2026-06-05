"""add category to recipes

Revision ID: e3c4d5f6a1b2
Revises: d2b3c4e5f6a1
Create Date: 2026-06-05 12:02:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "e3c4d5f6a1b2"  # pragma: allowlist secret
down_revision: str | Sequence[str] | None = "d2b3c4e5f6a1"  # pragma: allowlist secret
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "recipes",
        sa.Column("category_id", sa.UUID(), nullable=True),
    )
    op.create_foreign_key(
        "fk_recipes_category_id",
        "recipes",
        "categories",
        ["category_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        op.f("ix_recipes_category_id"), "recipes", ["category_id"], unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_recipes_category_id"), table_name="recipes")
    op.drop_constraint("fk_recipes_category_id", "recipes", type_="foreignkey")
    op.drop_column("recipes", "category_id")
