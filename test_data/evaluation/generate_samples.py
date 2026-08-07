import json
from pathlib import Path


OUTPUT_PATH = Path(__file__).resolve().parent / "generated" / "education_samples.json"
OUTCOMES = ["成交", "流失", "持续跟进"]
LEVEL_BY_OUTCOME = {"成交": "高", "流失": "低", "持续跟进": "中等"}


def generate_samples(count: int = 20) -> list[dict]:
    samples = []
    for index in range(1, count + 1):
        outcome = OUTCOMES[(index - 1) % len(OUTCOMES)]
        samples.append(
            {
                "sample_id": f"EDU-EVAL-{index:03d}",
                "analysis_record_id": index,
                "conversation_external_id": f"EDU-CONVERSATION-{index:04d}",
                "actual_outcome": outcome,
                "expected_customer_level": LEVEL_BY_OUTCOME[outcome],
                "expected_profile": {
                    "需求": ["提升学习成绩"],
                    "痛点": ["担心课程效果"],
                    "预算": "5000-8000元",
                    "购买阶段": (
                        "已成交" if outcome == "成交" else "流失" if outcome == "流失" else "方案评估"
                    ),
                    "意向等级": LEVEL_BY_OUTCOME[outcome],
                    "风险": ["明确拒绝"] if outcome == "流失" else [],
                },
            }
        )
    return samples


def main() -> None:
    samples = generate_samples()
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(
        json.dumps(samples, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    outcome_counts = {
        outcome: sum(item["actual_outcome"] == outcome for item in samples)
        for outcome in OUTCOMES
    }
    print(f"samples={len(samples)} outcomes={outcome_counts} output={OUTPUT_PATH}")


if __name__ == "__main__":
    main()
