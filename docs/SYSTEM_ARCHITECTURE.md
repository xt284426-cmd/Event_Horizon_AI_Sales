# 系统架构设计

## 架构概览

- API 层：FastAPI，负责 HTTP 接口与数据校验
- 服务层：承载后续业务编排与领域逻辑
- 数据层：SQLAlchemy 访问 PostgreSQL
- 迁移层：Alembic 管理数据库结构变更
- 前端：预留 Vue 3 独立应用
- 部署：Docker Compose 管理本地基础服务

## 当前状态

系统已建立客户查询 API、客户服务和 AI 分析查询服务。API 层通过 FastAPI 依赖注入获取 SQLAlchemy Session，服务层组合客户、画像、评分和最新 AI 分析结果。

## 当前查询链路

`Customer Router → CustomerService → AnalysisQueryService / SQLAlchemy → PostgreSQL`
