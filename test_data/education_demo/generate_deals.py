from datetime import datetime, timedelta, timezone

from test_data.education_demo.common import isoformat, seeded_random, write_json
from test_data.education_demo.generate_sales import generate_sales


COURSES = ["初中数学系统提升班", "高中英语冲刺班", "中考全科规划班", "高考一对一冲刺课", "小学学习习惯训练营"]
AMOUNTS = [4980, 6980, 8800, 12800, 16800, 19800]


def generate_deals(count: int = 25) -> list[dict]:
    rng = seeded_random(300)
    sales = generate_sales()
    base_time = datetime(2026, 2, 1, 10, 0, tzinfo=timezone.utc)
    deals = []
    for index in range(1, count + 1):
        salesperson = sales[(index - 1) % len(sales)]
        cycle_days = rng.randint(3, 28)
        closed_at = base_time + timedelta(days=index * 3)
        course = rng.choice(COURSES)
        deals.append(
            {
                "customer_external_id": f"EDU-CUSTOMER-{index:04d}",
                "sales_external_id": salesperson["external_user_id"],
                "amount": rng.choice(AMOUNTS),
                "currency": "CNY",
                "closed_at": isoformat(closed_at),
                "course_name": course,
                "title": course,
                "stage": "won",
                "sales_cycle_days": cycle_days,
                "started_at": isoformat(closed_at - timedelta(days=cycle_days)),
            }
        )
    return deals


def main() -> None:
    records = generate_deals()
    path = write_json("deals.json", records)
    print(f"deals={len(records)} output={path}")


if __name__ == "__main__":
    main()
