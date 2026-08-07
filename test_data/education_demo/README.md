# 教育行业模拟数据

该目录生成符合当前 SQLAlchemy 模型关系的教育行业销售演示数据，用于后续 AI 分析模块开发。所有姓名、电话、邮箱和业务内容均为模拟信息。

## 数据规模

- 3 名销售人员
- 100 名客户
- 100 个会话
- 1200 条聊天消息
- 25 条成交记录

生成器使用固定随机种子和稳定外部 ID。同一数据库重复执行时，会更新相同销售、客户、会话和消息；成交记录以客户、课程和成交时间联合识别，不会重复创建。

## 字段映射

- 客户年级、成绩、目标、关注点、预算和购买阶段存入 `customers.extra_data`。
- 聊天通过 `conversations.customer_id` 与 `owner_user_id` 关联客户和销售，消息意图及双方外部 ID 存入 `conversation_messages.raw_data`。
- 成交课程映射到 `deals.title`，成交周期用于生成会话开始与成交时间，完整演示字段保留在 `generated/deals.json`。
- 销售部门、等级、工作年限和擅长领域保留在 `generated/sales.json`；数据库仅写入当前 `users` 表已有字段。

## 运行

仅生成 JSON：

```bash
python -m test_data.education_demo.seed_database --generate-only
```

写入 PostgreSQL 前先执行迁移，然后设置连接地址：

```bash
alembic upgrade head
export DATABASE_URL="postgresql+psycopg2://event_horizon:change_me@localhost:5432/event_horizon_ai_sales"
python -m test_data.education_demo.seed_database
```

PowerShell 设置环境变量：

```powershell
$env:DATABASE_URL = "postgresql+psycopg2://event_horizon:change_me@localhost:5432/event_horizon_ai_sales"
python -m test_data.education_demo.seed_database
```
