from fastapi import APIRouter

from src.views.auth import router as auth_router
from src.views.favorites import router as favorites_router

master_router = APIRouter()
master_router.include_router(auth_router)
master_router.include_router(favorites_router)
