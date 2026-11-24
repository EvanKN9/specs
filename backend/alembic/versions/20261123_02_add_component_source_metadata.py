"""Add source identity and licensing metadata to components.

Revision ID: 20261123_02
Revises: 20261123_01
Create Date: 2026-11-23
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "20261123_02"
down_revision: Union[str, None] = "20261123_01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("components", sa.Column("source_id", sa.String(length=160), nullable=True))
    op.add_column("components", sa.Column("source_license", sa.String(length=80), nullable=True))
    op.add_column("components", sa.Column("source_license_url", sa.Text(), nullable=True))
    op.add_column("components", sa.Column("source_attribution", sa.Text(), nullable=True))
    op.create_unique_constraint(
        "uq_components_source_identity",
        "components",
        ["source_name", "source_id"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_components_source_identity", "components", type_="unique")
    op.drop_column("components", "source_attribution")
    op.drop_column("components", "source_license_url")
    op.drop_column("components", "source_license")
    op.drop_column("components", "source_id")
