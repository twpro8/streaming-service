from uuid import UUID

from fastapi import APIRouter, Path

from src.services.episodes import EpisodeService
from src.api.dependencies import AdminDep, DBDep, EpisodesParamsDep
from src.schemas.episodes import EpisodeAddDTO, EpisodePatchRequestDTO

from src.exceptions import (
    SeriesNotFoundException,
    SeasonNotFoundException,
    EpisodeNotFoundException,
    EpisodeAlreadyExistsException,
    SeriesNotFoundHTTPException,
    SeasonNotFoundHTTPException,
    EpisodeNotFoundHTTPException,
    EpisodeAlreadyExistsHTTPException,
    UniqueEpisodePerSeasonException,
    UniqueEpisodePerSeasonHTTPException,
    UniqueFileURLHTTPException,
    UniqueFileURLException,
)


router = APIRouter(prefix="/episodes", tags=["Episodes"])


@router.get("", summary="Get episodes")
async def get_episodes(db: DBDep, episodes_params: EpisodesParamsDep):
    episodes = await EpisodeService(db).get_episodes(**episodes_params.model_dump())
    return {"status": "ok", "data": episodes}


@router.get("/{episode_id}")
async def get_episode(db: DBDep, episode_id: UUID):
    try:
        episode = await EpisodeService(db).get_episode(episode_id=episode_id)
    except EpisodeNotFoundException:
        raise EpisodeNotFoundHTTPException
    return {"status": "ok", "data": episode}


@router.post("", dependencies=[AdminDep], status_code=201)
async def add_episode(db: DBDep, episode_data: EpisodeAddDTO):
    try:
        episode = await EpisodeService(db).add_episode(episode_data)
    except SeriesNotFoundException:
        raise SeriesNotFoundHTTPException
    except SeasonNotFoundException:
        raise SeasonNotFoundHTTPException
    except EpisodeAlreadyExistsException:
        raise EpisodeAlreadyExistsHTTPException
    except UniqueEpisodePerSeasonException:
        raise UniqueEpisodePerSeasonHTTPException
    except UniqueFileURLException:
        raise UniqueFileURLHTTPException
    return {"status": "ok", "data": episode}


@router.patch("/{episode_id}", dependencies=[AdminDep])
async def update_episode(
    db: DBDep,
    episode_data: EpisodePatchRequestDTO,
    episode_id: UUID = Path(),
):
    try:
        await EpisodeService(db).update_episode(episode_id=episode_id, data=episode_data)
    except EpisodeNotFoundException:
        raise EpisodeNotFoundHTTPException
    except UniqueEpisodePerSeasonException:
        raise UniqueEpisodePerSeasonHTTPException
    except UniqueFileURLException:
        raise UniqueFileURLHTTPException
    return {"status": "ok"}


@router.delete("/{episode_id}", dependencies=[AdminDep], status_code=204)
async def delete_episode(db: DBDep, episode_id: UUID = Path()):
    await EpisodeService(db).delete_episode(episode_id=episode_id)
