from fastapi import APIRouter, Depends, Request
from app.core.auth import get_current_user_id
from app.models.schemas import DashboardResponse, WorkoutHistoryItem, WeeklyTrendItem, SUPPORTED_GOALS
from app.services.database import get_user_history
from collections import defaultdict
from datetime import timedelta

router = APIRouter()

@router.get("/dashboard", response_model=DashboardResponse, summary="Get Dashboard Analytics")
async def get_dashboard(request: Request, user_id: str = Depends(get_current_user_id)):
    """
    Computes dashboard metrics based strictly on explicit completions (DASH-01 to DASH-07, AT-21).
    """
    records = await get_user_history(user_id, request.state.supabase_access_token)
    
    # 1. Total Completed
    total_completed = len(records)

    # 2. Recent Activity (up to 5 most recent)
    recent_activity = [
        WorkoutHistoryItem(
            id=r["id"],
            workout_id=r["workout_id"],
            completed_at=r["completed_at"],
            session_name=r.get("session_name", "Workout Session"),
            primary_goal=r.get("primary_goal", "General fitness")
        )
        for r in records[:5]
    ]

    # 3. Goal-wise counts
    goal_counts = {g: 0 for g in SUPPORTED_GOALS}
    for r in records:
        g = r.get("primary_goal", "General fitness")
        if g in goal_counts:
            goal_counts[g] += 1
        else:
            goal_counts[g] = 1

    # 4. Weekly trends
    weekly_map = defaultdict(int)
    for r in records:
        dt = r["completed_at"]
        # Find start of week (Monday)
        start_of_week = (dt - timedelta(days=dt.weekday())).strftime("%Y-%m-%d")
        weekly_map[start_of_week] += 1

    sorted_weeks = sorted(weekly_map.keys())
    weekly_trends = [
        WeeklyTrendItem(week_start=w, completion_count=weekly_map[w])
        for w in sorted_weeks
    ]

    return DashboardResponse(
        total_completed=total_completed,
        recent_activity=recent_activity,
        weekly_trends=weekly_trends,
        goal_wise_counts=goal_counts
    )
