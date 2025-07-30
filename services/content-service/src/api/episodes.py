from uuid import UUID

from fastapi import APIRouter, Path

from src.exceptions import EpisodeNotFoundException, EpisodeNotFoundHTTPException
from src.services.episodes import EpisodeService
from src.utils.decorators import handle_episode_exceptions
from src.api.dependencies import AdminDep, DBDep, EpisodesParamsDep
from src.schemas.episodes import EpisodeAddDTO, EpisodePatchRequestDTO


router = APIRouter(prefix="/episodes", tags=["Episodes"])


@router.get("", summary="Get episodes")
@handle_episode_exceptions
async def get_episodes(db: DBDep, episodes_params: EpisodesParamsDep):
    episodes = await EpisodeService(db).get_episodes(**episodes_params)
    return {"status": "ok", "data": episodes}


@router.get("/{episode_id}")
async def get_episode(db: DBDep, episode_id: UUID):
    try:
        episode = await EpisodeService(db).get_episode(episode_id=episode_id)
    except EpisodeNotFoundException:
        raise EpisodeNotFoundHTTPException
    return {"status": "ok", "data": episode}


@router.post("", dependencies=[AdminDep], status_code=201)
@handle_episode_exceptions
async def add_new_episode(db: DBDep, episode_data: EpisodeAddDTO):
    episode = await EpisodeService(db).add_episode(episode_data)
    return {"status": "ok", "data": episode}


@router.patch("/{episode_id}", dependencies=[AdminDep])
@handle_episode_exceptions
async def update_episode(
    db: DBDep, episode_data: EpisodePatchRequestDTO, episode_id: UUID = Path()
):
    await EpisodeService(db).update_episode(episode_id=episode_id, data=episode_data)
    return {"status": "ok"}


@router.delete("/{episode_id}", dependencies=[AdminDep], status_code=204)
async def delete_episode(db: DBDep, episode_id: UUID = Path()):
    await EpisodeService(db).delete_episode(episode_id=episode_id)
