from fastapi import APIRouter

from src.views.auth import router as auth_router

master_router = APIRouter()
master_router.include_router(auth_router)
