from fastapi import APIRouter

from src.api.movies import v1_router as v1_movies_router
from src.api.shows import v1_router as v1_shows_router
from src.api.seasons import v1_router as v1_seasons_router
from src.api.episodes import v1_router as v1_episodes_router
from src.api.comments import v1_router as v1_comments_router
from src.api.rating import v1_router as v1_rating_router
from src.api.genres import v1_router as v1_genres_router
from src.api.actors import v1_router as v1_actors_router
from src.api.metrics import router as metrics_router
from src.api.directors import v1_router as v1_directors_router

master_router = APIRouter()
master_router.include_router(v1_movies_router)
master_router.include_router(v1_shows_router)
master_router.include_router(v1_seasons_router)
master_router.include_router(v1_episodes_router)
master_router.include_router(v1_directors_router)
master_router.include_router(v1_actors_router)
master_router.include_router(v1_comments_router)
master_router.include_router(v1_rating_router)
master_router.include_router(v1_genres_router)
master_router.include_router(metrics_router)
