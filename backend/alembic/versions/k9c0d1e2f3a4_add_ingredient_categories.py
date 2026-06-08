"""add ingredient categories

Revision ID: k9c0d1e2f3a4
Revises: j8b9c0d1e2f3
Create Date: 2026-06-08 14:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

from alembic import op

revision: str = "k9c0d1e2f3a4"
down_revision: str | None = "j8b9c0d1e2f3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "ingredient_categories",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_ingredient_categories_name", "ingredient_categories", ["name"])

    op.add_column(
        "ingredients",
        sa.Column(
            "category_id",
            UUID(as_uuid=True),
            sa.ForeignKey("ingredient_categories.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_index("ix_ingredients_category_id", "ingredients", ["category_id"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_ingredients_category_id", table_name="ingredients")
    op.drop_column("ingredients", "category_id")
    op.drop_index("ix_ingredient_categories_name", table_name="ingredient_categories")
    op.drop_table("ingredient_categories")
