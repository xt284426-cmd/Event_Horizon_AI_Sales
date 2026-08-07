from pydantic import BaseModel, ConfigDict, Field


class AIOutputSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True, extra="forbid")


class CustomerProfileAnalysis(AIOutputSchema):
    needs: list[str] = Field(alias="需求", description="客户明确或隐含的学习需求")
    pain_points: list[str] = Field(alias="痛点", description="阻碍客户决策的核心问题")
    budget: str | None = Field(default=None, alias="预算")
    purchase_stage: str = Field(alias="购买阶段")
    intent_level: str = Field(alias="意向等级")
    risks: list[str] = Field(default_factory=list, alias="风险")


class SalesAnalysis(AIOutputSchema):
    strengths: list[str] = Field(default_factory=list, alias="优势")
    issues: list[str] = Field(default_factory=list, alias="问题")
    improvement_suggestions: list[str] = Field(default_factory=list, alias="改进建议")


class FollowSuggestion(AIOutputSchema):
    next_actions: list[str] = Field(default_factory=list, alias="下一步动作")
    recommended_script: str = Field(alias="推荐话术")


class ConversationAnalysisResult(AIOutputSchema):
    conversation_id: int
    customer_profile: CustomerProfileAnalysis
    sales_analysis: SalesAnalysis
    follow_suggestion: FollowSuggestion
    provider: str
    simulated: bool = False
    confidence: float | None = Field(default=None, ge=0, le=1)
