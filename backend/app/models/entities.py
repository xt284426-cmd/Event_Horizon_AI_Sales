from datetime import date, datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.db.base import Base, TimestampMixin


class Company(TimestampMixin, Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    users: Mapped[list["User"]] = relationship(back_populates="company")
    customers: Mapped[list["Customer"]] = relationship(back_populates="company")


class User(TimestampMixin, Base):
    __tablename__ = "users"
    __table_args__ = (UniqueConstraint("company_id", "external_user_id"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False
    )
    external_user_id: Mapped[str | None] = mapped_column(String(128))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(32), default="sales", server_default="sales")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    company: Mapped["Company"] = relationship(back_populates="users")
    conversations: Mapped[list["Conversation"]] = relationship(back_populates="owner")
    follow_records: Mapped[list["FollowRecord"]] = relationship(back_populates="user")


class Customer(TimestampMixin, Base):
    __tablename__ = "customers"
    __table_args__ = (UniqueConstraint("company_id", "external_customer_id"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False
    )
    external_customer_id: Mapped[str | None] = mapped_column(String(128))
    name: Mapped[str | None] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(String(32))
    email: Mapped[str | None] = mapped_column(String(255))
    source: Mapped[str | None] = mapped_column(String(64))
    status: Mapped[str] = mapped_column(String(32), default="new", server_default="new")
    extra_data: Mapped[dict[str, Any] | None] = mapped_column(JSONB)

    company: Mapped["Company"] = relationship(back_populates="customers")
    conversations: Mapped[list["Conversation"]] = relationship(back_populates="customer")
    profiles: Mapped[list["CustomerProfile"]] = relationship(back_populates="customer")
    analyses: Mapped[list["AIAnalysisRecord"]] = relationship(back_populates="customer")
    scores: Mapped[list["CustomerScore"]] = relationship(back_populates="customer")
    follow_records: Mapped[list["FollowRecord"]] = relationship(back_populates="customer")
    deals: Mapped[list["Deal"]] = relationship(back_populates="customer")


class Conversation(TimestampMixin, Base):
    __tablename__ = "conversations"
    __table_args__ = (UniqueConstraint("company_id", "external_conversation_id"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False
    )
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"), index=True, nullable=False
    )
    owner_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    external_conversation_id: Mapped[str | None] = mapped_column(String(128))
    channel: Mapped[str] = mapped_column(
        String(32), default="wecom", server_default="wecom"
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    customer: Mapped["Customer"] = relationship(back_populates="conversations")
    owner: Mapped["User | None"] = relationship(back_populates="conversations")
    messages: Mapped[list["ConversationMessage"]] = relationship(
        back_populates="conversation", order_by="ConversationMessage.sent_at"
    )


class ConversationMessage(TimestampMixin, Base):
    __tablename__ = "conversation_messages"
    __table_args__ = (
        UniqueConstraint("company_id", "external_message_id"),
        Index("ix_conversation_messages_conversation_sent", "conversation_id", "sent_at"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False
    )
    conversation_id: Mapped[int] = mapped_column(
        ForeignKey("conversations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    external_message_id: Mapped[str | None] = mapped_column(String(128))
    sender_type: Mapped[str] = mapped_column(String(32), nullable=False)
    sender_external_id: Mapped[str | None] = mapped_column(String(128))
    message_type: Mapped[str] = mapped_column(
        String(32), default="text", server_default="text"
    )
    content: Mapped[str | None] = mapped_column(Text)
    raw_data: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    conversation: Mapped["Conversation"] = relationship(back_populates="messages")


class ProfileTemplate(TimestampMixin, Base):
    __tablename__ = "profile_templates"
    __table_args__ = (UniqueConstraint("company_id", "name"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    version: Mapped[int] = mapped_column(Integer, default=1, server_default="1")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true")

    fields: Mapped[list["ProfileField"]] = relationship(back_populates="template")
    customer_profiles: Mapped[list["CustomerProfile"]] = relationship(
        back_populates="template"
    )


class ProfileField(TimestampMixin, Base):
    __tablename__ = "profile_fields"
    __table_args__ = (UniqueConstraint("template_id", "field_key"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False
    )
    template_id: Mapped[int] = mapped_column(
        ForeignKey("profile_templates.id", ondelete="CASCADE"), index=True, nullable=False
    )
    field_key: Mapped[str] = mapped_column(String(64), nullable=False)
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    field_type: Mapped[str] = mapped_column(String(32), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    options: Mapped[list[Any] | None] = mapped_column(JSONB)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    is_required: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")

    template: Mapped["ProfileTemplate"] = relationship(back_populates="fields")


class CustomerProfile(TimestampMixin, Base):
    __tablename__ = "customer_profiles"
    __table_args__ = (UniqueConstraint("customer_id", "template_id"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False
    )
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"), index=True, nullable=False
    )
    template_id: Mapped[int] = mapped_column(
        ForeignKey("profile_templates.id", ondelete="CASCADE"), index=True, nullable=False
    )
    profile_data: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    source: Mapped[str] = mapped_column(String(32), default="ai", server_default="ai")
    confidence: Mapped[Decimal | None] = mapped_column(Numeric(5, 4))

    customer: Mapped["Customer"] = relationship(back_populates="profiles")
    template: Mapped["ProfileTemplate"] = relationship(back_populates="customer_profiles")


class AIAnalysisRecord(TimestampMixin, Base):
    __tablename__ = "ai_analysis_records"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False
    )
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"), index=True, nullable=False
    )
    conversation_id: Mapped[int | None] = mapped_column(
        ForeignKey("conversations.id", ondelete="SET NULL"), index=True
    )
    analysis_type: Mapped[str] = mapped_column(String(64), nullable=False)
    model_name: Mapped[str | None] = mapped_column(String(128))
    model_version: Mapped[str | None] = mapped_column(String(64))
    input_reference: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    result: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    status: Mapped[str] = mapped_column(
        String(32), default="completed", server_default="completed"
    )
    error_message: Mapped[str | None] = mapped_column(Text)

    customer: Mapped["Customer"] = relationship(back_populates="analyses")


class CustomerScore(TimestampMixin, Base):
    __tablename__ = "customer_scores"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False
    )
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"), index=True, nullable=False
    )
    analysis_record_id: Mapped[int | None] = mapped_column(
        ForeignKey("ai_analysis_records.id", ondelete="SET NULL"), index=True
    )
    score_type: Mapped[str] = mapped_column(String(64), nullable=False)
    score: Mapped[Decimal] = mapped_column(Numeric(8, 4), nullable=False)
    level: Mapped[str | None] = mapped_column(String(32))
    factors: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    scored_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    customer: Mapped["Customer"] = relationship(back_populates="scores")


class FollowRecord(TimestampMixin, Base):
    __tablename__ = "follow_records"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False
    )
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"), index=True, nullable=False
    )
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    follow_type: Mapped[str] = mapped_column(String(32), nullable=False)
    content: Mapped[str | None] = mapped_column(Text)
    followed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    next_follow_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    customer: Mapped["Customer"] = relationship(back_populates="follow_records")
    user: Mapped["User | None"] = relationship(back_populates="follow_records")


class Deal(TimestampMixin, Base):
    __tablename__ = "deals"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    company_id: Mapped[int] = mapped_column(
        ForeignKey("companies.id", ondelete="CASCADE"), index=True, nullable=False
    )
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id", ondelete="CASCADE"), index=True, nullable=False
    )
    owner_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2))
    currency: Mapped[str] = mapped_column(String(3), default="CNY", server_default="CNY")
    stage: Mapped[str] = mapped_column(
        String(32), default="lead", server_default="lead"
    )
    expected_close_date: Mapped[date | None] = mapped_column(Date)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    lost_reason: Mapped[str | None] = mapped_column(Text)

    customer: Mapped["Customer"] = relationship(back_populates="deals")
