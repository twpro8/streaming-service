from fastapi import APIRouter

from src.adapters.service import ServiceAdapter
from src.config import settings
from src.exceptions import (
    FilmNotFoundException,
    FilmNotFoundHTTPException,
    AlreadyInFavoritesHTTPException,
    AlreadyInFavoritesException,
)
from src.schemas.favorites import FavoriteAddRequestDTO
from src.views.dependencies import DBDep, UserIdDep
from src.services.favorites import FavoriteService


router = APIRouter(prefix="/favorites", tags=["Favorites"])
adapter = ServiceAdapter(content_service_url=settings.CONTENT_SERVICE_URL)


@router.get("", summary="Get my favorites")
async def get_favorites(db: DBDep, user_id: UserIdDep):
    favorites = await FavoriteService(db, adapter).get_favorites(user_id=user_id)
    return {"status": "ok", "data": favorites}


@router.post("/{film_id}", summary="Add to favorites")
async def add_favorite(db: DBDep, user_id: UserIdDep, favorite: FavoriteAddRequestDTO):
    try:
        favorite = await FavoriteService(db, adapter).add_to_favorites(user_id, favorite)
    except FilmNotFoundException:
        raise FilmNotFoundHTTPException
    except AlreadyInFavoritesException:
        raise AlreadyInFavoritesHTTPException
    return {"status": "ok", "data": favorite}


@router.delete("/{film_id}", summary="Remove from favorites")
async def remove_favorite(db: DBDep, film_id: int):
    return {"status": "ok"}
