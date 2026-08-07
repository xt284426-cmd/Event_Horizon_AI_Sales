from collections.abc import Mapping, Sequence
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from backend.app.models import AiEvaluation
from backend.app.modules.ai_engine.evaluation_schemas import (
    EvaluationReport,
    EvaluationSample,
    MetricResult,
)


CUSTOMER_LEVEL_ACCURACY = "customer_level_accuracy"
DEAL_PREDICTION_ACCURACY = "deal_prediction_accuracy"
PROFILE_COMPLETENESS = "profile_completeness"
PROFILE_FIELDS = ("需求", "痛点", "预算", "购买阶段", "意向等级", "风险")


class AIEvaluationService:
    """Compare structured AI output with labeled business outcomes."""

    def __init__(self, session: Session | None = None) -> None:
        self._session = session

    def evaluate(
        self,
        analysis_results: Sequence[Mapping[str, Any]],
        samples: Sequence[EvaluationSample | Mapping[str, Any]],
        *,
        persist: bool = False,
    ) -> EvaluationReport:
        labels = [
            sample
            if isinstance(sample, EvaluationSample)
            else EvaluationSample.model_validate(sample)
            for sample in samples
        ]
        results_by_id = {
            int(result["analysis_record_id"]): result for result in analysis_results
        }
        metric_scores: dict[str, list[float]] = {
            CUSTOMER_LEVEL_ACCURACY: [],
            DEAL_PREDICTION_ACCURACY: [],
            PROFILE_COMPLETENESS: [],
        }

        for sample in labels:
            analysis = results_by_id.get(sample.analysis_record_id)
            if analysis is None:
                continue
            result_json = analysis.get("result", analysis)
            profile = result_json.get("customer_profile", {})

            actual_level = self._field(profile, "意向等级", "intent_level")
            level_score = float(actual_level == sample.expected_customer_level)
            self._record_metric(
                metric_scores,
                CUSTOMER_LEVEL_ACCURACY,
                level_score,
                sample,
                expected={"customer_level": sample.expected_customer_level},
                actual={"customer_level": actual_level},
                analysis=analysis,
                persist=persist,
            )

            predicted_outcome = self._predict_outcome(profile)
            deal_score = float(predicted_outcome == sample.actual_outcome)
            self._record_metric(
                metric_scores,
                DEAL_PREDICTION_ACCURACY,
                deal_score,
                sample,
                expected={"outcome": sample.actual_outcome},
                actual={"outcome": predicted_outcome},
                analysis=analysis,
                persist=persist,
            )

            completeness = self._profile_completeness(profile)
            self._record_metric(
                metric_scores,
                PROFILE_COMPLETENESS,
                completeness,
                sample,
                expected={"required_fields": list(PROFILE_FIELDS)},
                actual={"profile": profile},
                analysis=analysis,
                persist=persist,
            )

        if persist and self._session is not None:
            self._session.commit()

        metrics = []
        for name, scores in metric_scores.items():
            average = sum(scores) / len(scores) if scores else 0.0
            metrics.append(
                MetricResult(
                    metric_name=name,
                    score=round(average, 5),
                    evaluated_count=len(scores),
                )
            )
        return EvaluationReport(sample_count=len(labels), metrics=metrics)

    def _record_metric(
        self,
        metric_scores: dict[str, list[float]],
        metric_name: str,
        score: float,
        sample: EvaluationSample,
        *,
        expected: dict[str, Any],
        actual: dict[str, Any],
        analysis: Mapping[str, Any],
        persist: bool,
    ) -> None:
        metric_scores[metric_name].append(score)
        if not persist:
            return
        if self._session is None:
            raise ValueError("A SQLAlchemy session is required when persist=True")
        company_id = analysis.get("company_id")
        if company_id is None:
            raise ValueError("company_id is required to persist evaluation metrics")
        self._session.add(
            AiEvaluation(
                company_id=int(company_id),
                analysis_record_id=sample.analysis_record_id,
                metric_name=metric_name,
                expected_value=expected,
                actual_value=actual,
                score=Decimal(str(round(score, 5))),
            )
        )

    @staticmethod
    def _field(profile: Mapping[str, Any], alias: str, field_name: str) -> Any:
        return profile.get(alias, profile.get(field_name))

    @classmethod
    def _predict_outcome(cls, profile: Mapping[str, Any]) -> str:
        stage = str(cls._field(profile, "购买阶段", "purchase_stage") or "")
        level = str(cls._field(profile, "意向等级", "intent_level") or "")
        risks = cls._field(profile, "风险", "risks") or []
        risk_text = " ".join(str(item) for item in risks)
        if stage in {"已成交", "成交"} or level in {"高", "高意向"}:
            return "成交"
        if stage in {"流失", "已流失"} or "明确拒绝" in risk_text:
            return "流失"
        return "持续跟进"

    @classmethod
    def _profile_completeness(cls, profile: Mapping[str, Any]) -> float:
        values = [
            cls._field(
                profile,
                alias,
                {
                    "需求": "needs",
                    "痛点": "pain_points",
                    "预算": "budget",
                    "购买阶段": "purchase_stage",
                    "意向等级": "intent_level",
                    "风险": "risks",
                }[alias],
            )
            for alias in PROFILE_FIELDS
        ]
        present = sum(value is not None and value != "" for value in values)
        return present / len(PROFILE_FIELDS)
