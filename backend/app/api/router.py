from fastapi import APIRouter
from .content import router as content_router
from .analytics import router as analytics_router
from .users import router as users_router
from .auth import router as auth_router

# Create main API router
api_router = APIRouter()

# Include all routers
api_router.include_router(auth_router)  # Auth router first for login/register
api_router.include_router(content_router)
api_router.include_router(analytics_router)
api_router.include_router(users_router)
