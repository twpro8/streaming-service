from fastapi import APIRouter

from src.exceptions import (
    FilmNotFoundException,
    FilmNotFoundHTTPException,
    AlreadyInFavoritesHTTPException,
    AlreadyInFavoritesException,
)
from src.schemas.favorites import FavoriteAddRequestDTO
from src.views.dependencies import DBDep, UserIdDep, ACDep
from src.services.favorites import FavoriteService


router = APIRouter(prefix="/favorites", tags=["Favorites"])


@router.get("", summary="Get my favorites")
async def get_favorites(db: DBDep, ac: ACDep, user_id: UserIdDep):
    favorites = await FavoriteService(db, ac).get_favorites(user_id=user_id)
    return {"status": "success", "favorites": favorites}


@router.post("/{film_id}", summary="Add to favorites")
async def add_favorite(db: DBDep, ac: ACDep, user_id: UserIdDep, favorite: FavoriteAddRequestDTO):
    try:
        favorite = await FavoriteService(db, ac).add_to_favorites(user_id, favorite)
    except FilmNotFoundException:
        raise FilmNotFoundHTTPException
    except AlreadyInFavoritesException:
        raise AlreadyInFavoritesHTTPException
    return {"status": "success", "favorite": favorite}


@router.delete("/{film_id}", summary="Remove from favorites")
async def remove_favorite(db: DBDep, film_id: int):
    return {"status": "success"}
