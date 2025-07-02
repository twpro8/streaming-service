from fastapi import APIRouter

from src.api.dependencies import AdminDep
from src.api.images import router as image_router
from src.api.videos import router as video_router


master_router = APIRouter(dependencies=[AdminDep])
master_router.include_router(video_router)
master_router.include_router(image_router)
