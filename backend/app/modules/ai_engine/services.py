from enum import StrEnum
from decimal import Decimal

from sqlalchemy.orm import Session

from backend.app.models import AIAnalysisRecord, Conversation
from backend.app.modules.ai_engine.analyzer import ConversationAnalyzer
from backend.app.modules.ai_engine.conversation_loader import (
    ConversationLoader,
    ConversationNotFoundError,
)
from backend.app.modules.ai_engine.provider import AIProvider
from backend.app.modules.ai_engine.schemas import ConversationAnalysisResult


class AnalysisStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AIAnalysisService:
    """Load, analyze and persist a conversation using a caller-provided session."""

    def __init__(self, session: Session, provider: AIProvider | None = None) -> None:
        self._session = session
        self._loader = ConversationLoader(session)
        self._analyzer = ConversationAnalyzer(provider=provider)

    async def analyze_conversation(
        self,
        conversation_id: int,
    ) -> ConversationAnalysisResult:
        conversation = self._session.get(Conversation, conversation_id)
        if conversation is None:
            raise ConversationNotFoundError(
                f"Conversation {conversation_id} does not exist"
            )

        conversation_text = self._loader.load_conversation(conversation_id)
        record = AIAnalysisRecord(
            company_id=conversation.company_id,
            conversation_id=conversation.id,
            customer_id=conversation.customer_id,
            analysis_type="conversation_analysis",
            model_name="simulation",
            input_reference={"conversation_id": conversation.id},
            result={},
            status=AnalysisStatus.PENDING,
        )
        self._session.add(record)
        self._session.commit()
        record_id = record.id

        record.status = AnalysisStatus.RUNNING
        self._session.commit()

        try:
            result = await self._analyzer.analyze(
                conversation_id=conversation_id,
                conversation_text=conversation_text,
            )
            record.result = result.model_dump(mode="json", by_alias=True)
            record.confidence = (
                Decimal(str(result.confidence))
                if result.confidence is not None
                else None
            )
            record.model_name = result.provider
            record.status = AnalysisStatus.COMPLETED
            record.error_message = None
            self._session.commit()
            return result
        except Exception as exc:
            self._session.rollback()
            failed_record = self._session.get(AIAnalysisRecord, record_id)
            if failed_record is None:
                raise
            failed_record.status = AnalysisStatus.FAILED
            failed_record.error_message = str(exc)[:2000]
            self._session.commit()
            raise
