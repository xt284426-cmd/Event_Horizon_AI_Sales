# 系统架构设计

## 架构概览

- API 层：FastAPI，负责 HTTP 接口与数据校验
- 服务层：承载后续业务编排与领域逻辑
- 数据层：SQLAlchemy 访问 PostgreSQL
- 迁移层：Alembic 管理数据库结构变更
- 前端：预留 Vue 3 独立应用
- 部署：Docker Compose 管理本地基础服务

## 当前状态

仅建立分层目录和最小健康入口，具体模块边界将在后续设计阶段确定。
