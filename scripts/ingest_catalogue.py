"""Import the public Free Exercise DB records into Supabase as quarantined exercises."""

import json
from pathlib import Path
import sys
from typing import Any

from supabase import create_client

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.core.config import settings  # noqa: E402

SOURCE_URL = "https://github.com/yuhonas/free-exercise-db"
EQUIPMENT_MAP = {
    "body only": "Bodyweight only",
    "bodyweight": "Bodyweight only",
    "dumbbell": "Dumbbells",
    "dumbbells": "Dumbbells",
    "bands": "Resistance bands",
    "resistance band": "Resistance bands",
    "barbell": "Barbell",
    "bench": "Bench",
    "kettlebells": "Kettlebells",
    "kettlebell": "Kettlebells",
    "cable": "Cable machine",
    "machine": "Gym machines",
    "exercise ball": "Exercise ball",
    "foam roll": "Foam roller",
}
LEVEL_MAP = {"beginner": "Beginner", "intermediate": "Intermediate", "expert": "Advanced"}


def normalize_exercise(record: dict[str, Any]) -> dict[str, Any] | None:
    if not record.get("id") or not record.get("name"):
        return None
    equipment_value = record.get("equipment")
    equipment = EQUIPMENT_MAP.get(str(equipment_value or "").strip().lower())
    level = LEVEL_MAP.get(str(record.get("level") or "").lower())
    instructions = record.get("instructions")
    if not isinstance(instructions, list):
        instructions = [instructions] if instructions else []
    instructions = " ".join(str(part).strip() for part in instructions if part)
    muscles = record.get("primaryMuscles") or []
    if not isinstance(muscles, list):
        muscles = []
    secondary_muscles = record.get("secondaryMuscles") or []
    if not isinstance(secondary_muscles, list):
        secondary_muscles = []
    return {
        "exercise_id": str(record["id"]),
        "name": str(record["name"]).strip(),
        "difficulty": level,
        "equipment_requirements": [equipment] if equipment else [],
        "instructions": instructions,
        "primary_muscles": [str(value).title() for value in muscles],
        "secondary_muscles": [str(value).title() for value in secondary_muscles],
        "movement_pattern": record.get("force"),
        "exercise_category": str(record.get("category") or "general").title(),
        "source_reference": SOURCE_URL,
        "source_equipment": str(equipment_value) if equipment_value is not None else None,
        "source_level": str(record.get("level")) if record.get("level") is not None else None,
        "review_status": "quarantined",
    }


def import_catalogue(source_path: Path) -> tuple[int, int]:
    settings.require_service_role()
    records = json.loads(source_path.read_text(encoding="utf-8"))
    normalized = [item for raw in records if (item := normalize_exercise(raw))]
    skipped = len(records) - len(normalized)
    client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
    # Omitting review_status lets the table default quarantine new records and
    # prevents a refresh from changing an administrator's approval decision.
    payload = [{key: value for key, value in row.items() if key != "review_status"} for row in normalized]
    for offset in range(0, len(payload), 100):
        client.table("exercises").upsert(
            payload[offset:offset + 100], on_conflict="exercise_id"
        ).execute()
    return len(normalized), skipped


if __name__ == "__main__":
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "data" / "raw" / "exercises.json"
    try:
        imported, skipped = import_catalogue(path)
    except RuntimeError as error:
        print(error, file=sys.stderr)
        raise SystemExit(2)
    print(f"Imported {imported} source records as quarantined exercises; skipped {skipped} unmappable records.")
