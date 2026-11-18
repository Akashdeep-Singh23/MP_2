from fastapi import APIRouter, Depends, HTTPException, Request, status
from app.core.auth import get_current_user_id
from app.models.schemas import ProfileUpdateRequest, ProfileResponse
from app.services.safety import evaluate_safety_screening
from app.services.database import get_profile, save_profile
from datetime import datetime, timezone

router = APIRouter()

@router.get("/profile", response_model=ProfileResponse, summary="Get User Profile")
async def read_profile(request: Request, user_id: str = Depends(get_current_user_id)):
    """
    Retrieves the authenticated user's profile and minimal safety state.
    """
    profile = await get_profile(user_id, request.state.supabase_access_token)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "PROFILE_NOT_FOUND", "message": "Profile has not yet been initialized."}
        )
    return profile

@router.put("/profile", response_model=ProfileResponse, summary="Create or Update Profile")
async def update_profile(
    data: ProfileUpdateRequest,
    request: Request,
    user_id: str = Depends(get_current_user_id)
):
    """
    Creates or updates the user profile and evaluates mandatory physical screening answers.
    """
    safety_hold, screening_status = evaluate_safety_screening(
        data.screening_answers,
        data.confirm_cleared
    )

    profile_data = {
        "primary_goal": data.primary_goal,
        "fitness_level": data.fitness_level,
        "equipment": data.equipment,
        "available_duration_minutes": data.available_duration_minutes,
        "safety_hold": safety_hold,
        "safety_screening_status": screening_status,
        "safety_confirmed_at": datetime.now(timezone.utc)
    }

    saved = await save_profile(user_id, profile_data, request.state.supabase_access_token)
    return saved
