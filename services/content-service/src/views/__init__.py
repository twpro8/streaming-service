from fastapi import APIRouter

from src.views.films import router as films_router
from src.views.series import router as series_router


master_router = APIRouter()
master_router.include_router(films_router)
master_router.include_router(series_router)
