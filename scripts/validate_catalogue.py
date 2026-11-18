"""Validate real imported exercise data and approved workout coverage in Supabase."""

import asyncio
from pathlib import Path
import sys

import asyncpg

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from app.core.config import settings  # noqa: E402
from app.models.schemas import SUPPORTED_GOALS  # noqa: E402


async def validate_catalogue() -> bool:
    settings.require_database()
    connection = await asyncpg.connect(settings.DATABASE_URL, command_timeout=15)
    try:
        exercise_counts = await connection.fetchrow(
            """SELECT count(*) AS total,
                      count(*) FILTER (WHERE review_status = 'approved') AS approved,
                      count(*) FILTER (WHERE review_status = 'quarantined') AS quarantined,
                      count(*) FILTER (WHERE review_status = 'approved'
                        AND (name = '' OR instructions = '' OR cardinality(primary_muscles) = 0)) AS incomplete_approved
               FROM exercises"""
        )
        sessions = await connection.fetch(
            """SELECT ws.primary_goal, ws.workout_id, count(se.exercise_id) AS exercise_count,
                      count(e.exercise_id) AS approved_exercise_count
               FROM workout_sessions ws
               LEFT JOIN session_exercises se ON se.workout_id = ws.workout_id
               LEFT JOIN exercises e ON e.exercise_id = se.exercise_id AND e.review_status = 'approved'
               WHERE ws.review_status = 'approved'
               GROUP BY ws.workout_id"""
        )
    finally:
        await connection.close()

    print(f"Source exercises: {exercise_counts['total']} total; {exercise_counts['approved']} approved; {exercise_counts['quarantined']} quarantined")
    print(f"Incomplete approved rows: {exercise_counts['incomplete_approved']}")
    errors = []
    if exercise_counts["total"] == 0:
        errors.append("No source exercises are imported.")
    if exercise_counts["incomplete_approved"]:
        errors.append("Some approved exercises have missing required catalogue fields.")
    coverage = {goal: 0 for goal in SUPPORTED_GOALS}
    for session in sessions:
        if session["exercise_count"] == 0 or session["exercise_count"] != session["approved_exercise_count"]:
            errors.append(f"Approved session {session['workout_id']} has missing or unapproved exercises.")
        if session["primary_goal"] in coverage:
            coverage[session["primary_goal"]] += 1
    print("Approved session coverage:")
    for goal, count in coverage.items():
        print(f"  {goal}: {count}")
        if count < 5:
            errors.append(f"{goal} has {count} approved sessions; at least 5 are required.")
    if errors:
        print("Catalogue validation failed:")
        for error in errors:
            print(f"- {error}")
        return False
    print("Catalogue validation passed.")
    return True


if __name__ == "__main__":
    try:
        success = asyncio.run(validate_catalogue())
    except Exception as error:
        print(f"Catalogue validation could not run: {error}", file=sys.stderr)
        raise SystemExit(2)
    raise SystemExit(0 if success else 1)
