from test_data.education_demo.common import seeded_random, write_json


SURNAMES = "赵钱孙李周吴郑王冯陈褚卫蒋沈韩杨朱秦许何吕施张孔曹严华金魏陶姜谢邹喻柏水窦章"
GIVEN_NAMES = [
    "子轩", "雨桐", "梓涵", "浩然", "欣怡", "思远", "可馨", "宇航",
    "佳宁", "晨曦", "睿哲", "诗涵", "嘉怡", "俊熙", "若溪", "明轩",
]
SOURCES = ["企业微信自然咨询", "短视频广告", "公众号", "老客户转介绍", "线下活动", "搜索引擎"]
GRADES = ["小学三年级", "小学五年级", "初一", "初二", "初三", "高一", "高二", "高三"]
SCORES = ["基础薄弱（60分以下）", "中等（60-79分）", "良好（80-89分）", "优秀（90分以上）"]
GOALS = ["提高数学成绩", "英语冲刺提分", "改善学习习惯", "中考冲刺", "高考冲刺", "小升初衔接"]
CONCERNS = ["师资水平", "提分效果", "课程时间", "孩子接受程度", "价格与性价比", "学习反馈"]
BUDGETS = ["3000-5000元", "5000-8000元", "8000-12000元", "12000-20000元"]
STAGES = ["初次咨询", "需求确认", "方案比较", "价格沟通", "试听体验", "决策中", "已成交"]


def generate_customers(count: int = 100) -> list[dict]:
    rng = seeded_random(100)
    customers = []
    for index in range(1, count + 1):
        name = f"{rng.choice(SURNAMES)}{rng.choice(GIVEN_NAMES)}家长"
        stage = "已成交" if index <= 25 else rng.choice(STAGES[:-1])
        customers.append(
            {
                "external_customer_id": f"EDU-CUSTOMER-{index:04d}",
                "name": name,
                "phone": f"1{rng.choice([3, 5, 7, 8, 9])}{index:09d}"[-11:],
                "email": f"parent{index:04d}@example.test",
                "source": rng.choice(SOURCES),
                "status": "converted" if stage == "已成交" else "active",
                "extra_data": {
                    "child_grade": rng.choice(GRADES),
                    "current_score": rng.choice(SCORES),
                    "learning_goal": rng.choice(GOALS),
                    "parent_concern": rng.choice(CONCERNS),
                    "budget_range": rng.choice(BUDGETS),
                    "purchase_stage": stage,
                    "is_simulated": True,
                },
            }
        )
    return customers


def main() -> None:
    records = generate_customers()
    path = write_json("customers.json", records)
    print(f"customers={len(records)} output={path}")


if __name__ == "__main__":
    main()
