from fastapi import APIRouter, Depends, HTTPException, Request, status
from app.core.auth import get_current_user_id
from app.models.schemas import WorkoutHistoryCreate, WorkoutHistoryItem, WorkoutHistoryListResponse
from app.services.database import record_workout_completion, get_user_history, get_approved_session

router = APIRouter()

@router.get("/history", response_model=WorkoutHistoryListResponse, summary="Get Workout History")
async def read_history(request: Request, user_id: str = Depends(get_current_user_id)):
    """
    Returns the authenticated user's workout completion records ordered newest first.
    """
    records = await get_user_history(user_id, request.state.supabase_access_token)
    items = [
        WorkoutHistoryItem(
            id=r["id"],
            workout_id=r["workout_id"],
            completed_at=r["completed_at"],
            session_name=r.get("session_name", "Workout Session"),
            primary_goal=r.get("primary_goal", "General fitness")
        )
        for r in records
    ]
    return WorkoutHistoryListResponse(history=items, total_count=len(items))

@router.post("/history", response_model=WorkoutHistoryItem, status_code=status.HTTP_201_CREATED, summary="Log Workout Completion")
async def log_completion(
    data: WorkoutHistoryCreate,
    request: Request,
    user_id: str = Depends(get_current_user_id)
):
    """
    Records explicit workout completion with duplicate prevention (HIST-01 - HIST-04, AT-19, AT-20).
    """
    token = request.state.supabase_access_token
    target_session = await get_approved_session(data.workout_id, user_id, token)
    if target_session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "WORKOUT_NOT_FOUND", "message": "The approved workout session was not found."},
        )

    snapshot = {
        "workout_id": data.workout_id,
        "name": target_session["name"],
        "primary_goal": target_session["primary_goal"],
        "duration_minutes": target_session["duration_minutes"]
    }

    entry = await record_workout_completion(
        user_id=user_id,
        workout_id=data.workout_id,
        session_snapshot=snapshot,
        access_token=token,
        idempotency_key=data.idempotency_key
    )

    return WorkoutHistoryItem(
        id=entry["id"],
        workout_id=entry["workout_id"],
        completed_at=entry["completed_at"],
        session_name=entry["session_name"],
        primary_goal=entry["primary_goal"]
    )
