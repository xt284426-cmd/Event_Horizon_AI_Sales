"""SQLAlchemy model package."""

from backend.app.models.entities import (
    AIAnalysisRecord,
    Company,
    Conversation,
    ConversationMessage,
    Customer,
    CustomerProfile,
    CustomerScore,
    Deal,
    FollowRecord,
    ProfileField,
    ProfileTemplate,
    User,
)

__all__ = [
    "AIAnalysisRecord",
    "Company",
    "Conversation",
    "ConversationMessage",
    "Customer",
    "CustomerProfile",
    "CustomerScore",
    "Deal",
    "FollowRecord",
    "ProfileField",
    "ProfileTemplate",
    "User",
]
