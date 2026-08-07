from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


CustomerOutcome = Literal["成交", "流失", "持续跟进"]


class EvaluationSample(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sample_id: str
    analysis_record_id: int
    conversation_external_id: str
    actual_outcome: CustomerOutcome
    expected_customer_level: str
    expected_profile: dict[str, Any]


class MetricResult(BaseModel):
    metric_name: str
    score: float = Field(ge=0, le=1)
    evaluated_count: int = Field(ge=0)


class EvaluationReport(BaseModel):
    sample_count: int
    metrics: list[MetricResult]

    @property
    def accuracy(self) -> dict[str, float]:
        return {metric.metric_name: metric.score for metric in self.metrics}
