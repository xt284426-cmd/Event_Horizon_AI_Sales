# 数据库设计

## 技术选型

- PostgreSQL
- SQLAlchemy ORM
- Alembic 数据库迁移

## 设计状态

第一版数据库模型已建立，共 12 张表。全部表包含 `id`、`created_at` 和 `updated_at`；除租户根表 `companies` 外，其余表均包含 `company_id`，用于租户隔离和未来扩展。

## 第一版表结构

- `companies`：企业租户
- `users`：企业销售及系统用户
- `customers`：客户主数据
- `conversations`：客户与销售的会话
- `conversation_messages`：原始会话消息
- `profile_templates`：客户画像模板
- `profile_fields`：画像模板字段
- `customer_profiles`：客户画像实例及结构化画像数据
- `ai_analysis_records`：AI 分析过程和结果记录
- `customer_scores`：客户价值等评分记录
- `follow_records`：销售跟进记录
- `deals`：销售商机与成交记录

结构化扩展数据和 AI 结果使用 PostgreSQL JSONB；金额与分数使用定点数类型。外部系统标识在租户范围内设置唯一约束，常用外键均建立索引。

## 设计原则

- 原始聊天数据与分析结果分层存储
- 敏感信息最小化采集并支持脱敏
- 关键业务数据保留审计字段
- 所有结构变更通过 Alembic 迁移管理

## 后续设计事项

- 明确企业微信数据映射及幂等导入策略
- 增加数据访问层的租户隔离约束
- 评审敏感信息加密、脱敏与数据保留周期
- 根据查询模式补充复合索引和归档策略
