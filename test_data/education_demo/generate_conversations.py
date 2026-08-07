from datetime import datetime, timedelta, timezone

from test_data.education_demo.common import isoformat, seeded_random, write_json
from test_data.education_demo.generate_customers import generate_customers
from test_data.education_demo.generate_sales import generate_sales


TURN_TEMPLATES = [
    ("customer", "course_inquiry", "您好，我想了解一下适合{grade}孩子的课程。"),
    ("sales", "needs_discovery", "您好，我先了解一下，孩子现在的成绩和主要学习目标是什么？"),
    ("customer", "needs_expression", "目前{score}，希望能{goal}，我们比较关注{concern}。"),
    ("sales", "product_intro", "结合孩子情况，建议先做一次测评，再安排针对性的分层课程。"),
    ("customer", "price_inquiry", "这个课程怎么收费？我们的预算大概是{budget}。"),
    ("sales", "price_explanation", "费用会根据课时和班型确定，我给您按预算整理两套方案，价格都透明。"),
    ("customer", "objection", "我担心上了之后效果不明显，而且孩子时间也比较紧。"),
    ("sales", "case_study", "理解您的顾虑。类似基础的学员经过阶段计划后，通常先改善薄弱点，我们每周同步学习反馈。"),
    ("customer", "hesitation", "听起来还可以，不过我想再和家里人商量一下，也对比一下其他机构。"),
    ("sales", "closing", "没问题。我先为孩子保留试听和测评名额，体验后再决定，不会影响您比较。"),
    ("customer", "decision", "那先安排试听吧，如果孩子适应，我们就按推荐方案报名。"),
    ("sales", "closing", "好的，我马上发送预约信息和课程方案，之后全程协助您完成安排。"),
]


def generate_conversations(customer_count: int = 100) -> dict[str, list[dict]]:
    rng = seeded_random(200)
    customers = generate_customers(customer_count)
    sales = generate_sales()
    base_time = datetime(2026, 1, 5, 9, 0, tzinfo=timezone.utc)
    conversations: list[dict] = []
    messages: list[dict] = []

    for customer_index, customer in enumerate(customers, start=1):
        salesperson = sales[(customer_index - 1) % len(sales)]
        started_at = base_time + timedelta(days=customer_index % 90, hours=customer_index % 8)
        conversation_external_id = f"EDU-CONVERSATION-{customer_index:04d}"
        conversations.append(
            {
                "external_conversation_id": conversation_external_id,
                "customer_external_id": customer["external_customer_id"],
                "sales_external_id": salesperson["external_user_id"],
                "channel": "wecom",
                "started_at": isoformat(started_at),
                "ended_at": isoformat(started_at + timedelta(minutes=75)),
            }
        )
        context = {
            "grade": customer["extra_data"]["child_grade"],
            "score": customer["extra_data"]["current_score"],
            "goal": customer["extra_data"]["learning_goal"],
            "concern": customer["extra_data"]["parent_concern"],
            "budget": customer["extra_data"]["budget_range"],
        }
        elapsed = 0
        for turn, (sender_type, intent, template) in enumerate(TURN_TEMPLATES, start=1):
            elapsed += rng.randint(2, 9)
            sender_id = (
                customer["external_customer_id"]
                if sender_type == "customer"
                else salesperson["external_user_id"]
            )
            messages.append(
                {
                    "external_message_id": f"EDU-MESSAGE-{customer_index:04d}-{turn:02d}",
                    "conversation_external_id": conversation_external_id,
                    "customer_external_id": customer["external_customer_id"],
                    "sales_external_id": salesperson["external_user_id"],
                    "sender_type": sender_type,
                    "sender_external_id": sender_id,
                    "message_type": "text",
                    "content": template.format(**context),
                    "raw_data": {"intent": intent, "is_simulated": True},
                    "sent_at": isoformat(started_at + timedelta(minutes=elapsed)),
                }
            )
    return {"conversations": conversations, "messages": messages}


def main() -> None:
    result = generate_conversations()
    conversation_path = write_json("conversations.json", result["conversations"])
    message_path = write_json("messages.json", result["messages"])
    print(
        f"conversations={len(result['conversations'])} messages={len(result['messages'])} "
        f"outputs={conversation_path},{message_path}"
    )


if __name__ == "__main__":
    main()
