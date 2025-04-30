from fastapi import APIRouter

from src.views.films import router as films_router
from src.views.series import router as router
from src.views.seasons import router as seasons_router
from src.views.episodes import router as episodes_router
from src.views.comments import router as comments_router
from src.views.metrics import router as metrics_router

master_router = APIRouter()
master_router.include_router(films_router)
master_router.include_router(router)
master_router.include_router(seasons_router)
master_router.include_router(episodes_router)
master_router.include_router(comments_router)
master_router.include_router(metrics_router)
