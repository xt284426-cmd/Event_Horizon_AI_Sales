from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models import Conversation, ConversationMessage


class ConversationNotFoundError(LookupError):
    """Raised when the requested conversation does not exist."""


class ConversationLoader:
    """Load and normalize PostgreSQL conversation messages for AI analysis."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def load_conversation(self, conversation_id: int) -> str:
        if conversation_id <= 0:
            raise ValueError("conversation_id must be a positive integer")

        conversation = self._session.get(Conversation, conversation_id)
        if conversation is None:
            raise ConversationNotFoundError(
                f"Conversation {conversation_id} does not exist"
            )

        messages = self._session.scalars(
            select(ConversationMessage)
            .where(ConversationMessage.conversation_id == conversation_id)
            .order_by(ConversationMessage.sent_at, ConversationMessage.id)
        ).all()

        lines = []
        for message in messages:
            sender = "客户" if message.sender_type == "customer" else "销售"
            sender_id = message.sender_external_id or "unknown"
            sent_at = message.sent_at.isoformat()
            content = (message.content or "").strip()
            lines.append(f"[{sent_at}] {sender}({sender_id}): {content}")
        return "\n".join(lines)
