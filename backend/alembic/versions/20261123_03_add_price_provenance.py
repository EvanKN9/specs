"""Add explicit price provenance fields.

Revision ID: 20261123_03
Revises: 20261123_02
Create Date: 2026-11-23
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20261123_03"
down_revision: Union[str, None] = "20261123_02"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("components", sa.Column("price_source", sa.String(length=160), nullable=True))
    op.add_column(
        "components",
        sa.Column("price_is_illustrative", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.alter_column("components", "price_is_illustrative", server_default=None)


def downgrade() -> None:
    op.drop_column("components", "price_is_illustrative")
    op.drop_column("components", "price_source")
