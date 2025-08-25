from uuid import UUID

from fastapi import APIRouter, Path

from src.services.episodes import EpisodeService
from src.api.dependencies import AdminDep, DBDep, EpisodesParamsDep
from src.schemas.episodes import EpisodePatchRequestDTO, EpisodeAddRequestDTO

from src.exceptions import (
    ShowNotFoundException,
    SeasonNotFoundException,
    EpisodeNotFoundException,
    EpisodeAlreadyExistsException,
    ShowNotFoundHTTPException,
    SeasonNotFoundHTTPException,
    EpisodeNotFoundHTTPException,
    EpisodeAlreadyExistsHTTPException,
    UniqueEpisodePerSeasonException,
    UniqueEpisodePerSeasonHTTPException,
    UniqueFileURLHTTPException,
    UniqueFileURLException,
)


v1_router = APIRouter(prefix="/v1/episodes", tags=["Episodes"])


@v1_router.get("", summary="Get episodes")
async def get_episodes(db: DBDep, episodes_params: EpisodesParamsDep):
    episodes = await EpisodeService(db).get_episodes(**episodes_params.model_dump())
    return {"status": "ok", "data": episodes}


@v1_router.get("/{episode_id}")
async def get_episode(db: DBDep, episode_id: UUID):
    try:
        episode = await EpisodeService(db).get_episode(episode_id=episode_id)
    except EpisodeNotFoundException:
        raise EpisodeNotFoundHTTPException
    return {"status": "ok", "data": episode}


@v1_router.post("", dependencies=[AdminDep], status_code=201)
async def add_episode(db: DBDep, episode_data: EpisodeAddRequestDTO):
    try:
        episode_id = await EpisodeService(db).add_episode(episode_data)
    except ShowNotFoundException:
        raise ShowNotFoundHTTPException
    except SeasonNotFoundException:
        raise SeasonNotFoundHTTPException
    except EpisodeAlreadyExistsException:
        raise EpisodeAlreadyExistsHTTPException
    except UniqueEpisodePerSeasonException:
        raise UniqueEpisodePerSeasonHTTPException
    except UniqueFileURLException:
        raise UniqueFileURLHTTPException
    return {"status": "ok", "data": {"id": episode_id}}


@v1_router.patch("/{episode_id}", dependencies=[AdminDep])
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


@v1_router.delete("/{episode_id}", dependencies=[AdminDep], status_code=204)
async def delete_episode(db: DBDep, episode_id: UUID = Path()):
    await EpisodeService(db).delete_episode(episode_id=episode_id)
