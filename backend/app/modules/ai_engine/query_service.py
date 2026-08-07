from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models import AIAnalysisRecord


class AnalysisQueryService:
    """Read completed AI analysis records without exposing persistence details."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def get_latest_customer_analysis(
        self, customer_id: int
    ) -> AIAnalysisRecord | None:
        return self._session.scalar(
            select(AIAnalysisRecord)
            .where(
                AIAnalysisRecord.customer_id == customer_id,
                AIAnalysisRecord.status == "completed",
            )
            .order_by(AIAnalysisRecord.created_at.desc(), AIAnalysisRecord.id.desc())
            .limit(1)
        )
