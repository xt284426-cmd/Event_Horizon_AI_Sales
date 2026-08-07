from collections.abc import Mapping, Sequence
from typing import Any

from pydantic import ValidationError

from backend.app.modules.ai_engine.prompts import load_prompt
from backend.app.modules.ai_engine.provider import (
    AIProvider,
    AIProviderError,
    AIProviderRequest,
)
from backend.app.modules.ai_engine.schemas import (
    ConversationAnalysisResult,
    CustomerProfileAnalysis,
    FollowSuggestion,
    SalesAnalysis,
)


class ConversationAnalyzer:
    """Provider-independent entry point for structured conversation analysis."""

    def __init__(self, provider: AIProvider | None = None) -> None:
        self._provider = provider

    async def analyze(
        self,
        conversation_id: int,
        conversation_text: str = "",
        messages: Sequence[Mapping[str, Any]] = (),
    ) -> ConversationAnalysisResult:
        if conversation_id <= 0:
            raise ValueError("conversation_id must be a positive integer")

        if self._provider is None:
            return self._simulate(conversation_id)

        prompt = load_prompt("conversation_analysis.txt").format(
            conversation_id=conversation_id
        )
        if conversation_text:
            prompt = f"{prompt}\n\n待分析聊天记录：\n{conversation_text}"
        request = AIProviderRequest(
            conversation_id=conversation_id,
            prompt=prompt,
            conversation_text=conversation_text,
            messages=messages,
            response_schema=ConversationAnalysisResult.model_json_schema(),
        )
        response = await self._provider.analyze(request)
        payload = dict(response.structured_output)
        payload.update(
            conversation_id=conversation_id,
            provider=self._provider.provider_name,
            simulated=False,
        )
        try:
            return ConversationAnalysisResult.model_validate(payload)
        except ValidationError as exc:
            raise AIProviderError("Provider returned invalid structured output") from exc

    @staticmethod
    def _simulate(conversation_id: int) -> ConversationAnalysisResult:
        """Return deterministic sample output without calling an external model."""

        return ConversationAnalysisResult(
            conversation_id=conversation_id,
            customer_profile=CustomerProfileAnalysis(
                needs=["提升当前薄弱学科成绩", "获得阶段性学习规划"],
                pain_points=["担心课程效果", "可安排时间有限"],
                budget="待进一步确认",
                purchase_stage="方案评估",
                intent_level="中等",
                risks=["仍在比较其他机构", "关键决策人尚未完全确认"],
            ),
            sales_analysis=SalesAnalysis(
                strengths=["主动进行需求挖掘", "能够回应效果顾虑"],
                issues=["预算确认不够具体", "缺少明确的跟进时间"],
                improvement_suggestions=["补充量化学习方案", "约定下一次沟通节点"],
            ),
            follow_suggestion=FollowSuggestion(
                next_actions=["发送课程方案与案例", "24小时内确认试听时间"],
                recommended_script=(
                    "我已根据孩子目前的情况整理了两套方案，稍后发您对比。"
                    "我们也可以先确定试听时间，体验后再决定更适合的班型。"
                ),
            ),
            provider="simulation",
            simulated=True,
            confidence=0.75,
        )
