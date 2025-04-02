from fastapi import APIRouter

from src.views.dependencies import DBDep, UserIdDep, ACDep
from src.services.favorites import FavoriteService


router = APIRouter(prefix="/favorites", tags=["Favorites"])


@router.get("")
async def get_favorites(db: DBDep, ac: ACDep, user_id: UserIdDep):
    favorites = await FavoriteService(db, ac).get_favorites(user_id=user_id)
    return {"status": "success", "favorites": favorites}


@router.post("/{film_id}")
async def add_favorite(db: DBDep, user_id: UserIdDep, film_id: int):
    favorite = await FavoriteService(db).add_to_favorites(user_id=user_id, film_id=film_id)
    return {"status": "success", "favorite": favorite}
