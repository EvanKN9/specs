"""Create the initial components table.

Revision ID: 20261123_01
Revises:
Create Date: 2026-11-23
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20261123_01"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "components",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column(
            "category",
            sa.Enum(
                "cpu",
                "gpu",
                "motherboard",
                "memory",
                "storage",
                "psu",
                "case",
                "cpu_cooler",
                name="component_category",
                native_enum=False,
                length=32,
            ),
            nullable=False,
        ),
        sa.Column("manufacturer", sa.String(length=120), nullable=False),
        sa.Column("model_name", sa.String(length=200), nullable=False),
        sa.Column("specifications", sa.JSON(), nullable=False),
        sa.Column("price", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("source_name", sa.String(length=160), nullable=True),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("source_updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "category IN ('cpu', 'gpu', 'motherboard', 'memory', 'storage', 'psu', 'case', 'cpu_cooler')",
            name="ck_components_category",
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("components")
