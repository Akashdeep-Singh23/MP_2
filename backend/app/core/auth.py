from functools import lru_cache

from fastapi import HTTPException, Request, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from starlette.concurrency import run_in_threadpool
from supabase import create_client
from supabase_auth.errors import AuthApiError

from app.core.config import settings

security = HTTPBearer(auto_error=False)


@lru_cache(maxsize=1)
def _auth_client():
    settings.require_supabase_auth()
    return create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)

async def get_current_user_id(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Security(security),
) -> str:
    """
    Validates Supabase Bearer JWT and extracts the authoritative user_id from token claims ('sub').
    Rejects missing, expired, or malformed tokens with HTTP 401.
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "MISSING_TOKEN", "message": "Authorization header with Bearer token is required."}
        )

    try:
        settings.require_supabase_auth()
    except RuntimeError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "AUTH_NOT_CONFIGURED", "message": "Supabase Auth is not configured."},
        )
    
    try:
        result = await run_in_threadpool(_auth_client().auth.get_user, credentials.credentials)
        user = result.user
        if not user or not user.id:
            raise ValueError("Supabase returned no authenticated user")
        request.state.supabase_access_token = credentials.credentials
        return str(user.id)
    except AuthApiError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "INVALID_TOKEN", "message": "Could not validate credentials."}
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"code": "AUTH_UNAVAILABLE", "message": "Supabase Auth could not be reached."}
        )
