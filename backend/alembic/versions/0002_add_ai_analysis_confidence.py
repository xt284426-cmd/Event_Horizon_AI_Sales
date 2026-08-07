"""Add AI analysis confidence and lifecycle default.

Revision ID: 0002_ai_confidence
Revises: 0001_initial
Create Date: 2026-08-03
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0002_ai_confidence"
down_revision: str | None = "0001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "ai_analysis_records",
        sa.Column("confidence", sa.Numeric(5, 4), nullable=True),
    )
    op.alter_column(
        "ai_analysis_records",
        "status",
        existing_type=sa.String(length=32),
        server_default="pending",
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "ai_analysis_records",
        "status",
        existing_type=sa.String(length=32),
        server_default="completed",
        existing_nullable=False,
    )
    op.drop_column("ai_analysis_records", "confidence")
