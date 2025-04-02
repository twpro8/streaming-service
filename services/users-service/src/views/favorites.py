from fastapi import APIRouter

from src.exceptions import (
    FilmNotFoundException,
    FilmNotFoundHTTPException,
    AlreadyInFavoritesHTTPException,
    AlreadyInFavoritesException,
)
from src.views.dependencies import DBDep, UserIdDep, ACDep
from src.services.favorites import FavoriteService


router = APIRouter(prefix="/favorites", tags=["Favorites"])


@router.get("")
async def get_my_favorites(db: DBDep, ac: ACDep, user_id: UserIdDep):
    favorites = await FavoriteService(db, ac).get_favorites(user_id=user_id)
    return {"status": "success", "favorites": favorites}


@router.post("/{film_id}")
async def add_favorite(db: DBDep, ac: ACDep, user_id: UserIdDep, film_id: int):
    try:
        favorite = await FavoriteService(db, ac).add_to_favorites(user_id=user_id, film_id=film_id)
    except FilmNotFoundException:
        raise FilmNotFoundHTTPException
    except AlreadyInFavoritesException:
        raise AlreadyInFavoritesHTTPException
    return {"status": "success", "favorite": favorite}
