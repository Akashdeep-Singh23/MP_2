from fastapi import APIRouter
from datetime import datetime, timezone
from fastapi import HTTPException, status
from app.services.database import check_database

router = APIRouter()

@router.get("/health", summary="Health Check")
async def health_check():
    """
    Returns API health status, version, and server timestamp without leaking sensitive credentials.
    """
    try:
        await check_database()
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "DATABASE_UNAVAILABLE", "message": "Database readiness check failed."},
        )
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0"
    }
