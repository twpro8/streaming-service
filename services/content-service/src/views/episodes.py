from fastapi import APIRouter

from src.services.episodes import EpisodeService
from src.utils.decorators import handle_episode_exceptions
from src.views.dependencies import AdminDep, DBDep, PaginationDep
from src.schemas.episodes import EpisodeAddDTO, EpisodePatchRequestDTO, EpisodeDeleteRequestDTO


router = APIRouter(prefix="/episodes", tags=["Episodes"])


@router.get("", summary="Get episodes")
@handle_episode_exceptions
async def get_episodes(
    db: DBDep,
    pagination: PaginationDep,
    series_id: int,
    season_id: int = None,
    episode_title: str = None,
    episode_number: int = None,
):
    episodes = await EpisodeService(db).get_episodes(
        series_id=series_id,
        season_id=season_id,
        episode_title=episode_title,
        episode_number=episode_number,
        page=pagination.page,
        per_page=pagination.per_page,
    )
    return {"status": "ok", "data": episodes}


@router.post("", dependencies=[AdminDep])
@handle_episode_exceptions
async def add_new_episode(db: DBDep, episode_data: EpisodeAddDTO):
    episode = await EpisodeService(db).add_episode(episode_data)
    return {"status": "ok", "data": episode}


@router.patch("/{episode_id}", dependencies=[AdminDep])
@handle_episode_exceptions
async def update_episode(db: DBDep, episode_id: int, episode_data: EpisodePatchRequestDTO):
    await EpisodeService(db).update_episode(episode_id=episode_id, data=episode_data)
    return {"status": "ok"}


@router.delete("/{episode_id}", dependencies=[AdminDep])
@handle_episode_exceptions
async def delete_episode(db: DBDep, episode_id: int, episode_data: EpisodeDeleteRequestDTO):
    await EpisodeService(db).delete_episode(episode_id=episode_id, data=episode_data)
    return {"status": "ok"}
