from fastapi import APIRouter

from src.exceptions import (
    ContentNotFoundException,
    ContentNotFoundHTTPException,
    AlreadyInFavoritesHTTPException,
    AlreadyInFavoritesException,
    FavoriteNotFoundException,
    FavoriteNotFoundHTTPException,
)
from src.schemas.favorites import FavoriteAddRequestDTO
from src.views.dependencies import DBDep, UserIdDep
from src.services.favorites import FavoriteService


router = APIRouter(prefix="/favorites", tags=["Favorites"])


@router.get("", summary="Get my favorites")
async def get_favorites(db: DBDep, user_id: UserIdDep):
    favorites = await FavoriteService(db).get_favorites(user_id=user_id)
    return {"status": "ok", "data": favorites}


@router.post("/{film_id}", summary="Add to favorites")
async def add_favorite(db: DBDep, user_id: UserIdDep, favorite: FavoriteAddRequestDTO):
    try:
        favorite = await FavoriteService(db).add_to_favorites(user_id, favorite)
    except ContentNotFoundException:
        raise ContentNotFoundHTTPException
    except AlreadyInFavoritesException:
        raise AlreadyInFavoritesHTTPException
    return {"status": "ok", "data": favorite}


@router.delete("/{favorite_id}", summary="Remove from favorites")
async def remove_favorite(db: DBDep, user_id: UserIdDep, favorite_id: int):
    try:
        await FavoriteService(db).remove_favorite(user_id=user_id, favorite_id=favorite_id)
    except FavoriteNotFoundException:
        raise FavoriteNotFoundHTTPException
    return {"status": "ok"}
