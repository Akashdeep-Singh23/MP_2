from fastapi import APIRouter, Depends, HTTPException, Request, status
from app.core.auth import get_current_user_id
from app.models.schemas import AccountDeleteRequest
from app.services.database import delete_auth_user

router = APIRouter()

@router.delete("/account", summary="Delete Account & Private Data")
async def delete_account(
    data: AccountDeleteRequest,
    request: Request,
    user_id: str = Depends(get_current_user_id)
):
    """
    Permanently purges authenticated user's private data (profile and history)
    after deliberate confirmation (DEL-01 to DEL-07, AT-22).
    Shared catalogue remains untouched.
    """
    if data.confirmation != "DELETE_MY_ACCOUNT":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "CONFIRMATION_REQUIRED",
                "message": "Account deletion requires explicit confirmation string 'DELETE_MY_ACCOUNT'."
            }
        )

    try:
        await delete_auth_user(request.state.supabase_access_token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "ACCOUNT_DELETION_UNAVAILABLE", "message": "Account deletion is temporarily unavailable."},
        )

    return {
        "status": "success",
        "message": "Account and associated private data have been permanently deleted."
    }
