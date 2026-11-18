from fastapi import APIRouter
from app.api.endpoints import (
    health,
    profile,
    recommendations,
    history,
    dashboard,
    nutrition,
    account
)

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(profile.router, tags=["Profile"])
api_router.include_router(recommendations.router, tags=["Recommendations"])
api_router.include_router(history.router, tags=["History"])
api_router.include_router(dashboard.router, tags=["Dashboard"])
api_router.include_router(nutrition.router, tags=["Nutrition"])
api_router.include_router(account.router, tags=["Account"])
