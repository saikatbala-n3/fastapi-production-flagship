from fastapi import APIRouter

from app.api.v1.endpoints import health
from app.auth import routes
from app.users import routes

api_router = APIRouter()

# Include routers
api_router.include_router(health.router, tags=["health"])
api_router.include_router(routes.router, prefix="/auth", tags=["authentication"])
api_router.include_router(routes.router, prefix="/users", tags=["users"])
