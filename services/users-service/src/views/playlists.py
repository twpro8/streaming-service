from fastapi import APIRouter

from src.exceptions import (
    PlaylistAlreadyExistsException,
    PlaylistAlreadyExistsHTTPException,
    PlaylistNotFoundException,
    NoContentHTTPException,
)
from src.schemas.playlists import PlaylistAddRequestDTO
from src.services.playlists import PlaylistService
from src.views.dependencies import DBDep, UserIdDep, PaginationDep


router = APIRouter(prefix="/playlists", tags=["Playlists"])


@router.get("", summary="Get my playlists")
async def get_playlists(db: DBDep, user_id: UserIdDep, pagination: PaginationDep):
    playlists = await PlaylistService(db).get_playlists(
        user_id=user_id, page=pagination.page, per_page=pagination.per_page
    )
    return {"status": "ok", "data": playlists}


@router.post("", summary="Create an empty playlist")
async def add_playlist(db: DBDep, user_id: UserIdDep, playlist_data: PlaylistAddRequestDTO):
    try:
        playlist = await PlaylistService(db).add_playlist(user_id=user_id, data=playlist_data)
    except PlaylistAlreadyExistsException:
        raise PlaylistAlreadyExistsHTTPException
    return {"status": "ok", "data": playlist}


@router.delete("/{playlist_id}", summary="Remove a playlist")
async def remove_playlist(db: DBDep, user_id: UserIdDep, playlist_id: int):
    try:
        await PlaylistService(db).remove_playlist(user_id=user_id, playlist_id=playlist_id)
    except PlaylistNotFoundException:
        raise NoContentHTTPException
    return {"status": "ok"}
