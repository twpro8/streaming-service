from fastapi import APIRouter

from src.api.films import router as films_router
from src.api.series import router as router
from src.api.seasons import router as seasons_router
from src.api.episodes import router as episodes_router
from src.api.comments import router as comments_router
from src.api.rating import router as rating_router
from src.api.genres import router as genres_router
from src.api.actors import router as actors_router
from src.api.metrics import router as metrics_router

master_router = APIRouter()
master_router.include_router(films_router)
master_router.include_router(router)
master_router.include_router(seasons_router)
master_router.include_router(episodes_router)
master_router.include_router(comments_router)
master_router.include_router(rating_router)
master_router.include_router(genres_router)
master_router.include_router(actors_router)
master_router.include_router(metrics_router)
