from fastapi import APIRouter

from src.api.oauth import v1_router as oauth_router

master_router = APIRouter()
master_router.include_router(oauth_router)
