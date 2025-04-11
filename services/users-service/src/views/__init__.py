from fastapi import APIRouter

from src.views.auth import router as auth_router
from src.views.users import router as users_router
from src.views.favorites import router as favorites_router
from src.views.metrics import router as metrics_router

master_router = APIRouter()
master_router.include_router(auth_router)
master_router.include_router(users_router)
master_router.include_router(favorites_router)
master_router.include_router(metrics_router)
