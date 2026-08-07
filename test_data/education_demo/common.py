import json
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


RANDOM_SEED = 20260803
COMPANY_CODE = "education_demo"
COMPANY_NAME = "启航教育（模拟企业）"
OUTPUT_DIR = Path(__file__).resolve().parent / "generated"


def seeded_random(offset: int = 0) -> random.Random:
    return random.Random(RANDOM_SEED + offset)


def write_json(filename: str, data: Any) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / filename
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return path


def isoformat(value: datetime) -> str:
    return value.astimezone(timezone.utc).isoformat()
