"""Integration helpers for an explicitly designated disposable Supabase project."""

import os
import sys
import uuid
import asyncio
from urllib.parse import urlparse

import asyncpg
import pytest
from fastapi.testclient import TestClient
from supabase import create_client

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings  # noqa: E402
from app.main import app  # noqa: E402

_created_users: list[str] = []
_test_workout_ids = ["session-mg-01", "session-fl-01", "session-end-01"]


async def _delete_test_catalogue():
    connection = await asyncpg.connect(settings.DATABASE_URL)
    try:
        async with connection.transaction():
            await connection.execute("DELETE FROM workout_history WHERE workout_id = ANY($1::text[])", _test_workout_ids)
            await connection.execute("DELETE FROM workout_sessions WHERE workout_id = ANY($1::text[])", _test_workout_ids)
            await connection.execute("DELETE FROM exercises WHERE exercise_id LIKE 'codex-test-%'")
    finally:
        await connection.close()


async def _reset_test_catalogue():
    await _delete_test_catalogue()
    connection = await asyncpg.connect(settings.DATABASE_URL)
    try:
        async with connection.transaction():
            await connection.execute("DELETE FROM workout_sessions WHERE workout_id = ANY($1::text[])", _test_workout_ids)
            await connection.execute("DELETE FROM exercises WHERE exercise_id LIKE 'codex-test-%'")
            await connection.executemany(
                """INSERT INTO exercises
                   (exercise_id, name, difficulty, equipment_requirements, instructions, primary_muscles,
                    secondary_muscles, exercise_category, source_reference, review_status)
                   VALUES ($1,$2,$3,$4::text[],$5,$6::text[],$7::text[],$8,$9,'approved')""",
                [
                    ("codex-test-chest", "Test Chest Press", "Beginner", ["Dumbbells"], "Press with control.", ["Chest"], [], "Strength", "test-only fixture"),
                    ("codex-test-cardio", "Test Cardio March", "Beginner", ["Bodyweight only"], "March at a comfortable pace.", ["Cardio/Systemic"], [], "Cardio", "test-only fixture"),
                    ("codex-test-endurance", "Test Endurance Step", "Beginner", ["Bodyweight only"], "Step at a steady pace.", ["Legs"], [], "Cardio", "test-only fixture"),
                ],
            )
            await connection.executemany(
                """INSERT INTO workout_sessions
                   (workout_id,name,primary_goal,secondary_goals,difficulty,duration_minutes,required_equipment,
                    workout_type,instructions,source_attribution,review_status)
                   VALUES ($1,$2,$3,$4::text[],$5,$6,$7::text[],$8,$9,'test-only fixture','approved')""",
                [
                    ("session-mg-01", "Test Muscle Session", "Muscle gain", ["Strength improvement"], "Beginner", 30, ["Dumbbells"], "Strength", "Test fixture only."),
                    ("session-fl-01", "Test Fat Loss Session", "Fat loss", ["Endurance"], "Beginner", 25, ["Bodyweight only"], "Cardio", "Test fixture only."),
                    ("session-end-01", "Test Endurance Session", "Endurance", ["General fitness"], "Beginner", 30, ["Bodyweight only"], "Cardio", "Test fixture only."),
                ],
            )
            await connection.executemany(
                """INSERT INTO session_exercises
                   (workout_id,exercise_id,sequence_number,sets,reps,rest_seconds)
                   VALUES ($1,$2,1,2,'8',45)""",
                [("session-mg-01", "codex-test-chest"), ("session-fl-01", "codex-test-cardio"), ("session-end-01", "codex-test-endurance")],
            )
    finally:
        await connection.close()


def _admin_client():
    settings.require_service_role()
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)


@pytest.fixture(autouse=True)
def disposable_supabase_project(request):
    if request.path.name == "test_filtering_recommender.py":
        yield
        return
    if os.getenv("RUN_SUPABASE_INTEGRATION") != "1":
        pytest.skip("Set RUN_SUPABASE_INTEGRATION=1 only when backend/.env points to a disposable test project.")
    expected_project_ref = os.getenv("TEST_SUPABASE_PROJECT_REF")
    test_database_url = os.getenv("TEST_DATABASE_URL")
    configured_project_ref = urlparse(settings.SUPABASE_URL).hostname
    configured_project_ref = configured_project_ref.split(".")[0] if configured_project_ref else None
    if not expected_project_ref or configured_project_ref != expected_project_ref or not test_database_url:
        pytest.fail("Integration tests require a matching TEST_SUPABASE_PROJECT_REF and TEST_DATABASE_URL for a disposable project.")
    settings.DATABASE_URL = test_database_url
    settings.require_supabase_auth()
    settings.require_database()
    settings.require_service_role()
    _created_users.clear()
    asyncio.run(_reset_test_catalogue())
    yield
    admin = _admin_client()
    for user_id in _created_users:
        try:
            admin.auth.admin.delete_user(user_id)
        except Exception:
            pass  # Account-deletion tests may already have deleted this test user.
    _created_users.clear()
    asyncio.run(_delete_test_catalogue())


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def create_test_access_token(_label: str = "test-user", invalid: bool = False) -> str:
    if invalid:
        return "invalid.expired.test.token"
    admin = _admin_client()
    email = f"codex-test-{uuid.uuid4().hex}@example.com"
    password = f"T-{uuid.uuid4().hex}-Aa9!"
    created = admin.auth.admin.create_user({"email": email, "password": password, "email_confirm": True})
    user = created.user
    _created_users.append(user.id)
    signed_in = admin.auth.sign_in_with_password({"email": email, "password": password})
    return signed_in.session.access_token


@pytest.fixture
def auth_headers():
    return {"Authorization": f"Bearer {create_test_access_token()}"}
