from fastapi import APIRouter

from src.exceptions import (
    SeriesNotFoundException,
    SeasonNotFoundException,
    EpisodeNotFoundException,
    SeriesNotFoundHTTPException,
    SeasonNotFoundHTTPException,
    EpisodeAlreadyDeletedHTTPException,
    EpisodeNotFoundHTTPException,
    EpisodeAlreadyExistsException,
    EpisodeAlreadyExistsHTTPException,
)
from src.services.episodes import EpisodeService
from src.views.dependencies import AdminDep, DBDep, PaginationDep
from src.schemas.episodes import EpisodeAddDTO, EpisodePatchRequestDTO, EpisodeDeleteRequestDTO


router = APIRouter(prefix="/episodes", tags=["Episodes"])


@router.get("", summary="Get episodes")
async def get_episodes(
    db: DBDep,
    pagination: PaginationDep,
    series_id: int,
    season_id: int = None,
    episode_title: str = None,
    episode_number: int = None,
):
    try:
        episodes = await EpisodeService(db).get_episodes(
            series_id=series_id,
            season_id=season_id,
            episode_title=episode_title,
            episode_number=episode_number,
            page=pagination.page,
            per_page=pagination.per_page,
        )
    except SeriesNotFoundException:
        raise SeriesNotFoundHTTPException
    except SeasonNotFoundException:
        raise SeasonNotFoundHTTPException
    return {"status": "ok", "data": episodes}


@router.post("", dependencies=[AdminDep])
async def add_new_episode(db: DBDep, episode_data: EpisodeAddDTO):
    try:
        episode = await EpisodeService(db).add_episode(episode_data)
    except SeriesNotFoundException:
        raise SeriesNotFoundHTTPException
    except SeasonNotFoundException:
        raise SeasonNotFoundHTTPException
    except EpisodeAlreadyExistsException:
        raise EpisodeAlreadyExistsHTTPException
    return {"status": "ok", "data": episode}


@router.patch("/{episode_id}", dependencies=[AdminDep])
async def update_episode(db: DBDep, episode_id: int, episode_data: EpisodePatchRequestDTO):
    try:
        await EpisodeService(db).update_episode(episode_id=episode_id, data=episode_data)
    except SeriesNotFoundException:
        raise SeriesNotFoundHTTPException
    except SeasonNotFoundException:
        raise SeasonNotFoundHTTPException
    except EpisodeNotFoundException:
        raise EpisodeNotFoundHTTPException
    return {"status": "ok"}


@router.delete("/{episode_id}", dependencies=[AdminDep])
async def delete_episode(db: DBDep, episode_id: int, episode_data: EpisodeDeleteRequestDTO):
    try:
        await EpisodeService(db).delete_episode(episode_id=episode_id, data=episode_data)
    except SeriesNotFoundException:
        raise SeriesNotFoundHTTPException
    except SeasonNotFoundException:
        raise SeasonNotFoundHTTPException
    except EpisodeNotFoundException:
        raise EpisodeAlreadyDeletedHTTPException
    return {"status": "ok"}
