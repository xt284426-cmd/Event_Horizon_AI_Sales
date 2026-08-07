"""Create initial database models.

Revision ID: 0001_initial
Revises:
Create Date: 2026-08-03
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def timestamps() -> list[sa.Column]:
    return [
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
    ]


def company_id() -> sa.Column:
    return sa.Column(
        "company_id",
        sa.BigInteger(),
        sa.ForeignKey("companies.id", ondelete="CASCADE"),
        nullable=False,
    )


def upgrade() -> None:
    op.create_table(
        "companies",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("code", sa.String(64), nullable=False, unique=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        *timestamps(),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        company_id(),
        sa.Column("external_user_id", sa.String(128)),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("email", sa.String(255)),
        sa.Column("role", sa.String(32), server_default="sales", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        *timestamps(),
        sa.UniqueConstraint("company_id", "external_user_id"),
    )
    op.create_index("ix_users_company_id", "users", ["company_id"])

    op.create_table(
        "customers",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        company_id(),
        sa.Column("external_customer_id", sa.String(128)),
        sa.Column("name", sa.String(100)),
        sa.Column("phone", sa.String(32)),
        sa.Column("email", sa.String(255)),
        sa.Column("source", sa.String(64)),
        sa.Column("status", sa.String(32), server_default="new", nullable=False),
        sa.Column("extra_data", postgresql.JSONB()),
        *timestamps(),
        sa.UniqueConstraint("company_id", "external_customer_id"),
    )
    op.create_index("ix_customers_company_id", "customers", ["company_id"])

    op.create_table(
        "profile_templates",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        company_id(),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("version", sa.Integer(), server_default="1", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        *timestamps(),
        sa.UniqueConstraint("company_id", "name"),
    )
    op.create_index(
        "ix_profile_templates_company_id", "profile_templates", ["company_id"]
    )

    op.create_table(
        "conversations",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        company_id(),
        sa.Column(
            "customer_id",
            sa.BigInteger(),
            sa.ForeignKey("customers.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "owner_user_id",
            sa.BigInteger(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
        ),
        sa.Column("external_conversation_id", sa.String(128)),
        sa.Column("channel", sa.String(32), server_default="wecom", nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("ended_at", sa.DateTime(timezone=True)),
        *timestamps(),
        sa.UniqueConstraint("company_id", "external_conversation_id"),
    )
    op.create_index("ix_conversations_company_id", "conversations", ["company_id"])
    op.create_index("ix_conversations_customer_id", "conversations", ["customer_id"])
    op.create_index("ix_conversations_owner_user_id", "conversations", ["owner_user_id"])

    op.create_table(
        "profile_fields",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        company_id(),
        sa.Column(
            "template_id",
            sa.BigInteger(),
            sa.ForeignKey("profile_templates.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("field_key", sa.String(64), nullable=False),
        sa.Column("field_name", sa.String(100), nullable=False),
        sa.Column("field_type", sa.String(32), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("options", postgresql.JSONB()),
        sa.Column("sort_order", sa.Integer(), server_default="0", nullable=False),
        sa.Column("is_required", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        *timestamps(),
        sa.UniqueConstraint("template_id", "field_key"),
    )
    op.create_index("ix_profile_fields_company_id", "profile_fields", ["company_id"])
    op.create_index("ix_profile_fields_template_id", "profile_fields", ["template_id"])

    op.create_table(
        "conversation_messages",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        company_id(),
        sa.Column(
            "conversation_id",
            sa.BigInteger(),
            sa.ForeignKey("conversations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("external_message_id", sa.String(128)),
        sa.Column("sender_type", sa.String(32), nullable=False),
        sa.Column("sender_external_id", sa.String(128)),
        sa.Column("message_type", sa.String(32), server_default="text", nullable=False),
        sa.Column("content", sa.Text()),
        sa.Column("raw_data", postgresql.JSONB()),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=False),
        *timestamps(),
        sa.UniqueConstraint("company_id", "external_message_id"),
    )
    op.create_index(
        "ix_conversation_messages_company_id", "conversation_messages", ["company_id"]
    )
    op.create_index(
        "ix_conversation_messages_conversation_id",
        "conversation_messages",
        ["conversation_id"],
    )
    op.create_index(
        "ix_conversation_messages_conversation_sent",
        "conversation_messages",
        ["conversation_id", "sent_at"],
    )

    op.create_table(
        "customer_profiles",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        company_id(),
        sa.Column(
            "customer_id",
            sa.BigInteger(),
            sa.ForeignKey("customers.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "template_id",
            sa.BigInteger(),
            sa.ForeignKey("profile_templates.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("profile_data", postgresql.JSONB(), nullable=False),
        sa.Column("source", sa.String(32), server_default="ai", nullable=False),
        sa.Column("confidence", sa.Numeric(5, 4)),
        *timestamps(),
        sa.UniqueConstraint("customer_id", "template_id"),
    )
    op.create_index("ix_customer_profiles_company_id", "customer_profiles", ["company_id"])
    op.create_index("ix_customer_profiles_customer_id", "customer_profiles", ["customer_id"])
    op.create_index("ix_customer_profiles_template_id", "customer_profiles", ["template_id"])

    op.create_table(
        "ai_analysis_records",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        company_id(),
        sa.Column(
            "customer_id",
            sa.BigInteger(),
            sa.ForeignKey("customers.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "conversation_id",
            sa.BigInteger(),
            sa.ForeignKey("conversations.id", ondelete="SET NULL"),
        ),
        sa.Column("analysis_type", sa.String(64), nullable=False),
        sa.Column("model_name", sa.String(128)),
        sa.Column("model_version", sa.String(64)),
        sa.Column("input_reference", postgresql.JSONB()),
        sa.Column("result", postgresql.JSONB(), nullable=False),
        sa.Column("status", sa.String(32), server_default="completed", nullable=False),
        sa.Column("error_message", sa.Text()),
        *timestamps(),
    )
    op.create_index("ix_ai_analysis_records_company_id", "ai_analysis_records", ["company_id"])
    op.create_index("ix_ai_analysis_records_customer_id", "ai_analysis_records", ["customer_id"])
    op.create_index(
        "ix_ai_analysis_records_conversation_id", "ai_analysis_records", ["conversation_id"]
    )

    op.create_table(
        "customer_scores",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        company_id(),
        sa.Column(
            "customer_id",
            sa.BigInteger(),
            sa.ForeignKey("customers.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "analysis_record_id",
            sa.BigInteger(),
            sa.ForeignKey("ai_analysis_records.id", ondelete="SET NULL"),
        ),
        sa.Column("score_type", sa.String(64), nullable=False),
        sa.Column("score", sa.Numeric(8, 4), nullable=False),
        sa.Column("level", sa.String(32)),
        sa.Column("factors", postgresql.JSONB()),
        sa.Column("scored_at", sa.DateTime(timezone=True), nullable=False),
        *timestamps(),
    )
    op.create_index("ix_customer_scores_company_id", "customer_scores", ["company_id"])
    op.create_index("ix_customer_scores_customer_id", "customer_scores", ["customer_id"])
    op.create_index(
        "ix_customer_scores_analysis_record_id", "customer_scores", ["analysis_record_id"]
    )

    op.create_table(
        "follow_records",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        company_id(),
        sa.Column(
            "customer_id",
            sa.BigInteger(),
            sa.ForeignKey("customers.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id", sa.BigInteger(), sa.ForeignKey("users.id", ondelete="SET NULL")
        ),
        sa.Column("follow_type", sa.String(32), nullable=False),
        sa.Column("content", sa.Text()),
        sa.Column("followed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("next_follow_at", sa.DateTime(timezone=True)),
        *timestamps(),
    )
    op.create_index("ix_follow_records_company_id", "follow_records", ["company_id"])
    op.create_index("ix_follow_records_customer_id", "follow_records", ["customer_id"])
    op.create_index("ix_follow_records_user_id", "follow_records", ["user_id"])

    op.create_table(
        "deals",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        company_id(),
        sa.Column(
            "customer_id",
            sa.BigInteger(),
            sa.ForeignKey("customers.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "owner_user_id",
            sa.BigInteger(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
        ),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("amount", sa.Numeric(18, 2)),
        sa.Column("currency", sa.String(3), server_default="CNY", nullable=False),
        sa.Column("stage", sa.String(32), server_default="lead", nullable=False),
        sa.Column("expected_close_date", sa.Date()),
        sa.Column("closed_at", sa.DateTime(timezone=True)),
        sa.Column("lost_reason", sa.Text()),
        *timestamps(),
    )
    op.create_index("ix_deals_company_id", "deals", ["company_id"])
    op.create_index("ix_deals_customer_id", "deals", ["customer_id"])
    op.create_index("ix_deals_owner_user_id", "deals", ["owner_user_id"])


def downgrade() -> None:
    op.drop_table("deals")
    op.drop_table("follow_records")
    op.drop_table("customer_scores")
    op.drop_table("ai_analysis_records")
    op.drop_table("customer_profiles")
    op.drop_table("conversation_messages")
    op.drop_table("profile_fields")
    op.drop_table("conversations")
    op.drop_table("profile_templates")
    op.drop_table("customers")
    op.drop_table("users")
    op.drop_table("companies")
