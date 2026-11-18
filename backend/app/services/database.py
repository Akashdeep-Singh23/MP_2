"""Supabase Data API access. User-scoped queries carry the verified user's JWT into Postgres RLS."""

import json
from datetime import datetime
from typing import Any

import httpx
from starlette.concurrency import run_in_threadpool
from supabase import Client, create_client

from app.core.config import settings


class DatabaseUnavailable(Exception):
    """The configured Supabase Data API cannot be reached or configured."""


def _client(access_token: str | None = None) -> Client:
    settings.require_supabase_auth()
    client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)
    if access_token:
        client.postgrest.auth(access_token)
    return client


def _execute(query: Any) -> list[dict[str, Any]]:
    try:
        response = query.execute()
        return response.data or []
    except Exception as error:
        raise DatabaseUnavailable from error


async def check_database() -> None:
    """Check the REST-backed database without needing a Postgres password."""
    await run_in_threadpool(
        _execute,
        _client().table("exercises").select("exercise_id").limit(1),
    )


def _history_fields(row: dict[str, Any]) -> dict[str, Any]:
    item = dict(row)
    completed_at = item.get("completed_at")
    if isinstance(completed_at, str):
        item["completed_at"] = datetime.fromisoformat(completed_at.replace("Z", "+00:00"))
    snapshot = item.get("session_snapshot") or {}
    if isinstance(snapshot, str):
        try:
            snapshot = json.loads(snapshot)
        except (ValueError, TypeError):
            snapshot = {}
    item["session_name"] = snapshot.get("name", "Workout Session")
    item["primary_goal"] = snapshot.get("primary_goal", "General fitness")
    return item


async def get_profile(user_id: str, access_token: str) -> dict[str, Any] | None:
    client = _client(access_token)
    rows = await run_in_threadpool(
        _execute,
        client.table("profiles").select("*").eq("user_id", user_id).limit(1),
    )
    return rows[0] if rows else None


async def save_profile(
    user_id: str, profile_data: dict[str, Any], access_token: str
) -> dict[str, Any]:
    payload = {**profile_data, "user_id": user_id}
    confirmed_at = payload.get("safety_confirmed_at")
    if isinstance(confirmed_at, datetime):
        payload["safety_confirmed_at"] = confirmed_at.isoformat()
    rows = await run_in_threadpool(
        _execute,
        _client(access_token)
        .table("profiles")
        .upsert(payload, on_conflict="user_id")
        .select("*"),
    )
    if not rows:
        raise DatabaseUnavailable("Supabase returned no profile after upsert")
    return rows[0]


async def get_all_approved_sessions(
    user_id: str, access_token: str
) -> list[dict[str, Any]]:
    del user_id  # RLS scopes the request using the verified JWT.
    client = _client(access_token)
    sessions = await run_in_threadpool(
        _execute,
        client.table("workout_sessions").select("*").eq("review_status", "approved"),
    )
    if not sessions:
        return []

    session_ids = [row["workout_id"] for row in sessions]
    links = await run_in_threadpool(
        _execute,
        client.table("session_exercises")
        .select("workout_id,exercise_id,sequence_number,sets,reps,duration_seconds,rest_seconds,notes")
        .in_("workout_id", session_ids)
        .order("sequence_number"),
    )
    exercise_ids = sorted({row["exercise_id"] for row in links})
    exercises = []
    if exercise_ids:
        exercises = await run_in_threadpool(
            _execute,
            client.table("exercises")
            .select("exercise_id,name,instructions,primary_muscles")
            .in_("exercise_id", exercise_ids)
            .eq("review_status", "approved"),
        )
    exercise_by_id = {row["exercise_id"]: row for row in exercises}
    links_by_session: dict[str, list[dict[str, Any]]] = {}
    for link in links:
        links_by_session.setdefault(link["workout_id"], []).append(link)

    result = []
    for session in sessions:
        prescribed = links_by_session.get(session["workout_id"], [])
        if not prescribed or any(link["exercise_id"] not in exercise_by_id for link in prescribed):
            continue
        session["exercises"] = [
            {
                "sequence_number": link["sequence_number"],
                "exercise_id": link["exercise_id"],
                "name": exercise_by_id[link["exercise_id"]]["name"],
                "sets": link["sets"],
                "reps": link["reps"],
                "duration_seconds": link["duration_seconds"],
                "rest_seconds": link["rest_seconds"],
                "instructions": exercise_by_id[link["exercise_id"]]["instructions"],
                "notes": link.get("notes"),
                "primary_muscles": exercise_by_id[link["exercise_id"]]["primary_muscles"],
            }
            for link in prescribed
        ]
        result.append(session)
    return result


async def get_approved_session(
    workout_id: str, user_id: str, access_token: str
) -> dict[str, Any] | None:
    sessions = await get_all_approved_sessions(user_id, access_token)
    return next((session for session in sessions if session["workout_id"] == workout_id), None)


async def record_workout_completion(
    user_id: str,
    workout_id: str,
    session_snapshot: dict[str, Any],
    access_token: str,
    idempotency_key: str | None = None,
) -> dict[str, Any]:
    client = _client(access_token)
    if idempotency_key:
        prior = await run_in_threadpool(
            _execute,
            client.table("workout_history")
            .select("*")
            .eq("user_id", user_id)
            .eq("idempotency_key", idempotency_key)
            .limit(1),
        )
        if prior:
            return _history_fields(prior[0])

    try:
        rows = await run_in_threadpool(
            _execute,
            client.table("workout_history")
            .insert(
                {
                    "user_id": user_id,
                    "workout_id": workout_id,
                    "session_snapshot": session_snapshot,
                    "idempotency_key": idempotency_key,
                }
            )
            .select("*"),
        )
    except DatabaseUnavailable:
        if not idempotency_key:
            raise
        prior = await run_in_threadpool(
            _execute,
            client.table("workout_history")
            .select("*")
            .eq("user_id", user_id)
            .eq("idempotency_key", idempotency_key)
            .limit(1),
        )
        if prior:
            return _history_fields(prior[0])
        raise
    if not rows:
        raise DatabaseUnavailable("Supabase returned no history after insert")
    return _history_fields(rows[0])


async def get_user_history(user_id: str, access_token: str) -> list[dict[str, Any]]:
    rows = await run_in_threadpool(
        _execute,
        _client(access_token)
        .table("workout_history")
        .select("*")
        .eq("user_id", user_id)
        .order("completed_at", desc=True),
    )
    return [_history_fields(row) for row in rows]


async def delete_auth_user(access_token: str) -> None:
    settings.require_supabase_auth()
    try:
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(
                f"{settings.SUPABASE_URL.rstrip('/')}/functions/v1/delete-account",
                headers={
                    "apikey": settings.SUPABASE_ANON_KEY,
                    "Authorization": f"Bearer {access_token}",
                },
                json={},
            )
            response.raise_for_status()
    except Exception as error:
        raise DatabaseUnavailable from error
