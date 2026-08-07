"""Create AI evaluation metrics table.

Revision ID: 0003_ai_evaluations
Revises: 0002_ai_confidence
Create Date: 2026-08-03
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0003_ai_evaluations"
down_revision: str | None = "0002_ai_confidence"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "ai_evaluations",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column(
            "company_id",
            sa.BigInteger(),
            sa.ForeignKey("companies.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "analysis_record_id",
            sa.BigInteger(),
            sa.ForeignKey("ai_analysis_records.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("metric_name", sa.String(64), nullable=False),
        sa.Column("expected_value", postgresql.JSONB()),
        sa.Column("actual_value", postgresql.JSONB()),
        sa.Column("score", sa.Numeric(6, 5), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index("ix_ai_evaluations_company_id", "ai_evaluations", ["company_id"])
    op.create_index(
        "ix_ai_evaluations_analysis_record_id",
        "ai_evaluations",
        ["analysis_record_id"],
    )


def downgrade() -> None:
    op.drop_table("ai_evaluations")
