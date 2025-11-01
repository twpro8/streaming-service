from fastapi import APIRouter

from src.api.oauth import v1_router as oauth_router
from src.api.auth import v1_router as auth_router

master_router = APIRouter()
master_router.include_router(oauth_router)
master_router.include_router(auth_router)
