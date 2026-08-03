# Event_Horizon_AI_Sales

企业微信 AI 销售增长系统。项目将通过企业微信聊天数据分析，支持客户画像、客户价值判断、销售行为分析与成交优化。

## 技术架构

- 后端：Python 3.12、FastAPI
- 数据库：PostgreSQL
- ORM：SQLAlchemy
- 数据库迁移：Alembic
- 部署：Docker / Docker Compose
- 前端预留：Vue 3

当前目录采用前后端分离结构。`backend/app` 存放后端应用，`backend/alembic` 存放数据库迁移，`frontend` 为 Vue 3 前端预留目录，`docs` 存放产品和技术设计文档。

## 当前开发阶段

Phase 0：项目初始化。基础目录、最小 FastAPI 服务、依赖清单、PostgreSQL 容器和设计文档骨架已建立，尚未开发业务功能。

## 本地运行

1. 创建并激活 Python 3.12 虚拟环境。
2. 安装依赖：`pip install -r requirements.txt`。
3. 启动 PostgreSQL：`docker compose up -d postgres`。
4. 启动 API：`uvicorn backend.app.main:app --reload`。
5. 访问 `http://127.0.0.1:8000/`。

环境变量可参考 `.env.example`。

后续创建数据库模型后，可使用 `alembic revision --autogenerate -m "说明"` 生成迁移，并使用 `alembic upgrade head` 执行迁移。
