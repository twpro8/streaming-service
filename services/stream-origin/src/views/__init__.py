from fastapi import APIRouter

from src.views.stream import router as stream_router


master_router = APIRouter()
master_router.include_router(stream_router)
