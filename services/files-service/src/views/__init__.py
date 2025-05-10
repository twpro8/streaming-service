from fastapi import APIRouter

from src.views.files import router as files_router


master_router = APIRouter()
master_router.include_router(files_router)
