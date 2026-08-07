# AI 设计

## 目标能力

- 客户画像提取
- 客户价值判断
- 销售行为分析
- 成交优化建议

## 当前状态

AI 分析引擎已连接 PostgreSQL 会话数据，当前仅提供模拟分析，不调用真实 AI API。

## 模块边界

- `AIProvider`：统一模型接口，隔离 DeepSeek、通义千问、智谱及本地模型的调用差异
- `ConversationAnalyzer`：组装 Prompt、调用 Provider 并校验结构化输出
- `AIAnalysisService`：业务侧分析入口，后续负责会话读取和结果持久化编排
- Pydantic Schema：定义客户画像、销售表现和跟进建议的稳定输出契约
- Prompt 模板：独立文件管理，便于版本控制和评测
- `ConversationLoader`：查询会话消息，按发送时间排序并标准化为聊天文本
- `AIAnalysisRecord`：保存结构化结果、置信度及 pending/running/completed/failed 生命周期
- `AIEvaluationService`：将分析结果与人工标注的真实结果对比并聚合质量指标
- `AiEvaluation`：保存逐样本指标、期望值、实际值和得分

## 基础质量指标

- 客户等级准确率：AI 意向等级与标注等级一致的样本比例
- 成交预测准确率：成交、流失、持续跟进三分类结果的准确率
- 画像字段完整率：需求、痛点、预算、购买阶段、意向等级、风险六项字段的覆盖比例

## 后续设计事项

- 实现首个真实 Provider 适配器及配置管理
- 建立 Prompt 版本、模型版本、Token 用量和失败重试记录
- 扩充离线评估集，并建立指标基线、敏感数据脱敏和人工复核机制
