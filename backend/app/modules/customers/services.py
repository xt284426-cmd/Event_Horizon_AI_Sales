from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.app.models import (
    AIAnalysisRecord,
    Customer,
    CustomerProfile,
    CustomerScore,
)
from backend.app.modules.ai_engine.query_service import AnalysisQueryService
from backend.app.modules.customers.schemas import (
    AIAnalysisSummary,
    CustomerDetail,
    CustomerInfo,
    CustomerListItem,
)


class CustomerNotFoundError(LookupError):
    """Raised when a customer does not exist."""


class CustomerService:
    def __init__(self, session: Session) -> None:
        self._session = session
        self._analysis_queries = AnalysisQueryService(session)

    def list_customers(self, *, offset: int = 0, limit: int = 100) -> list[CustomerListItem]:
        latest_score = (
            select(CustomerScore.score)
            .where(CustomerScore.customer_id == Customer.id)
            .order_by(CustomerScore.scored_at.desc(), CustomerScore.id.desc())
            .limit(1)
            .correlate(Customer)
            .scalar_subquery()
        )
        latest_level = (
            select(CustomerScore.level)
            .where(CustomerScore.customer_id == Customer.id)
            .order_by(CustomerScore.scored_at.desc(), CustomerScore.id.desc())
            .limit(1)
            .correlate(Customer)
            .scalar_subquery()
        )
        latest_analysis_time = (
            select(AIAnalysisRecord.created_at)
            .where(
                AIAnalysisRecord.customer_id == Customer.id,
                AIAnalysisRecord.status == "completed",
            )
            .order_by(AIAnalysisRecord.created_at.desc(), AIAnalysisRecord.id.desc())
            .limit(1)
            .correlate(Customer)
            .scalar_subquery()
        )
        rows = self._session.execute(
            select(
                Customer.id,
                Customer.name,
                latest_level.label("level"),
                latest_score.label("latest_score"),
                latest_analysis_time.label("latest_ai_analysis_time"),
            )
            .order_by(Customer.id)
            .offset(offset)
            .limit(limit)
        ).mappings()
        return [
            CustomerListItem(
                id=row["id"],
                name=row["name"],
                level=row["level"],
                latest_score=(
                    float(row["latest_score"])
                    if row["latest_score"] is not None
                    else None
                ),
                latest_ai_analysis_time=row["latest_ai_analysis_time"],
            )
            for row in rows
        ]

    def get_customer_detail(self, customer_id: int) -> CustomerDetail:
        customer = self._session.get(Customer, customer_id)
        if customer is None:
            raise CustomerNotFoundError(f"Customer {customer_id} does not exist")

        profile_record = self._session.scalar(
            select(CustomerProfile)
            .where(CustomerProfile.customer_id == customer_id)
            .order_by(CustomerProfile.updated_at.desc(), CustomerProfile.id.desc())
            .limit(1)
        )
        analysis = self._analysis_queries.get_latest_customer_analysis(customer_id)
        analysis_result: dict[str, Any] = analysis.result if analysis else {}
        profile = (
            profile_record.profile_data
            if profile_record is not None
            else self._nested_dict(analysis_result, "customer_profile")
        )
        follow_suggestion = self._nested_dict(analysis_result, "follow_suggestion")

        analysis_summary = None
        if analysis is not None:
            analysis_summary = AIAnalysisSummary(
                id=analysis.id,
                analysis_type=analysis.analysis_type,
                status=analysis.status,
                confidence=(
                    float(analysis.confidence)
                    if analysis.confidence is not None
                    else None
                ),
                model_name=analysis.model_name,
                analyzed_at=analysis.created_at,
                result=analysis.result,
            )

        return CustomerDetail(
            customer=CustomerInfo.model_validate(customer),
            profile=profile,
            latest_ai_analysis=analysis_summary,
            follow_suggestion=follow_suggestion,
        )

    @staticmethod
    def _nested_dict(data: dict[str, Any], key: str) -> dict[str, Any]:
        value = data.get(key, {})
        return value if isinstance(value, dict) else {}
