from fastapi import APIRouter, Depends, HTTPException, Request, status
from app.core.auth import get_current_user_id
from app.models.schemas import RecommendationsResponse, WorkoutSessionItem
from app.services.database import get_profile, get_all_approved_sessions
from app.services.filtering import apply_hard_filters
from app.services.recommender import rank_sessions

router = APIRouter()

@router.post("/recommendations", response_model=RecommendationsResponse, summary="Get Workout Recommendations")
async def get_recommendations(request: Request, user_id: str = Depends(get_current_user_id)):
    """
    Evaluates safety status and eligibility, then runs content-based Cosine Similarity
    to return up to 5 personalized workout sessions.
    """
    token = request.state.supabase_access_token
    profile = await get_profile(user_id, token)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "PROFILE_INCOMPLETE",
                "message": "Please complete your mandatory fitness profile and safety screening first."
            }
        )

    # 1. Enforce Backend Safety Hold (SAFE-01 to SAFE-12, AT-08, AT-09)
    if profile.get("safety_hold") or profile.get("safety_screening_status") != "CLEARED":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "SAFETY_HOLD_ACTIVE",
                "message": "Personalized recommendations are currently paused due to an active safety hold or physical limitation.",
                "details": {
                    "status": profile.get("safety_screening_status", "HOLD"),
                    "action": "Please consult a healthcare professional or resolve safety screening before resuming."
                }
            }
        )

    # 2. Load Approved Candidate Sessions (DATA-06, REC-03, AT-07)
    candidates = await get_all_approved_sessions(user_id, token)

    # 3. Apply Hard Eligibility Filters (REC-04, REC-05, EQ-02)
    eligible = apply_hard_filters(
        candidates,
        user_level=profile.get("fitness_level"),
        user_equipment=profile.get("equipment", [])
    )

    # 4. Handle Empty Candidate Pool Cleanly (REC-15, AT-12)
    if not eligible:
        return RecommendationsResponse(
            results=[],
            message="No workout sessions currently match your exact equipment set and fitness level. Try adding additional equipment or adjusting your level."
        )

    # 5. Content-Based Cosine Similarity Ranking (REC-07, REC-13, REC-18)
    ranked = rank_sessions(eligible, profile, top_k=5)

    return RecommendationsResponse(
        results=ranked,
        message=f"Successfully generated {len(ranked)} personalized recommendation(s)."
    )
