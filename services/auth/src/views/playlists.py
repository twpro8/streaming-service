from fastapi import APIRouter

from src.exceptions import (
    PlaylistAlreadyExistsException,
    PlaylistAlreadyExistsHTTPException,
    PlaylistNotFoundException,
    NoContentHTTPException,
    PlaylistNotFoundHTTPException,
    PlaylistItemAlreadyExistsException,
    PlaylistItemAlreadyExistsHTTPException,
    PlaylistItemNotFoundException,
)
from src.schemas.playlists import PlaylistAddRequestDTO, PlaylistItemAddRequestDTO
from src.services.playlists import PlaylistService
from src.views.dependencies import DBDep, UserDep, PaginationDep


router = APIRouter(prefix="/playlists", tags=["Playlists"])


@router.get("", summary="Get my playlists")
async def get_playlists(db: DBDep, user_id: UserDep, pagination: PaginationDep):
    playlists = await PlaylistService(db).get_playlists(
        user_id=user_id, page=pagination.page, per_page=pagination.per_page
    )
    return {"status": "ok", "data": playlists}


@router.get("/{playlist_id}/items", summary="Get my playlist items")
async def get_items(db: DBDep, user_id: UserDep, pagination: PaginationDep, playlist_id: int):
    try:
        items = await PlaylistService(db).get_items(
            user_id=user_id,
            playlist_id=playlist_id,
            page=pagination.page,
            per_page=pagination.per_page,
        )
    except PlaylistNotFoundException:
        raise PlaylistNotFoundHTTPException
    return {"status": "ok", "data": items}


@router.post("", summary="Create an empty playlist")
async def add_playlist(db: DBDep, user_id: UserDep, playlist_data: PlaylistAddRequestDTO):
    try:
        playlist = await PlaylistService(db).add_playlist(user_id=user_id, data=playlist_data)
    except PlaylistAlreadyExistsException:
        raise PlaylistAlreadyExistsHTTPException
    return {"status": "ok", "data": playlist}


@router.post("/{playlist_id}/items", summary="Add an item to playlist")
async def add_item(
    db: DBDep, user_id: UserDep, playlist_id: int, item_data: PlaylistItemAddRequestDTO
):
    try:
        # before we have to check if content exists in content service
        item = await PlaylistService(db).add_item(
            user_id=user_id, playlist_id=playlist_id, data=item_data
        )
    except PlaylistNotFoundException:
        raise PlaylistNotFoundHTTPException
    except PlaylistItemAlreadyExistsException:
        raise PlaylistItemAlreadyExistsHTTPException
    return {"status": "ok", "data": item}


@router.delete("/{playlist_id}", summary="Remove a playlist")
async def remove_playlist(db: DBDep, user_id: UserDep, playlist_id: int):
    try:
        await PlaylistService(db).remove_playlist(user_id=user_id, playlist_id=playlist_id)
    except PlaylistNotFoundException:
        raise NoContentHTTPException
    return {"status": "ok"}


@router.delete("/{playlist_id}/items/{item_id}", summary="Remove an item from playlist")
async def remove_item(db: DBDep, user_id: UserDep, playlist_id: int, item_id: int):
    try:
        await PlaylistService(db).remove_item(
            user_id=user_id, playlist_id=playlist_id, item_id=item_id
        )
    except PlaylistNotFoundException:
        raise NoContentHTTPException
    except PlaylistItemNotFoundException:
        raise NoContentHTTPException
    return {"status": "ok"}
