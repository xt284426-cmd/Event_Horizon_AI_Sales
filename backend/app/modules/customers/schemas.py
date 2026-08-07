from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class CustomerSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class CustomerListItem(CustomerSchema):
    id: int
    name: str | None
    level: str | None
    latest_score: float | None
    latest_ai_analysis_time: datetime | None


class CustomerInfo(CustomerSchema):
    id: int
    name: str | None
    phone: str | None
    email: str | None
    source: str | None
    status: str
    extra_data: dict[str, Any] | None


class AIAnalysisSummary(CustomerSchema):
    id: int
    analysis_type: str
    status: str
    confidence: float | None
    model_name: str | None
    analyzed_at: datetime
    result: dict[str, Any]


class CustomerDetail(CustomerSchema):
    customer: CustomerInfo
    profile: dict[str, Any]
    latest_ai_analysis: AIAnalysisSummary | None
    follow_suggestion: dict[str, Any]
