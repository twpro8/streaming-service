from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from src.factories.service import ServiceFactory
from src.services.episodes import EpisodeService
from src.api.dependencies import AdminDep, EpisodesParamsDep
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


v1_router = APIRouter(prefix="/v1/episodes", tags=["episodes"])


@v1_router.get("", summary="Get episodes")
async def get_episodes(
    service: Annotated[EpisodeService, Depends(ServiceFactory.episode_service_factory)],
    episodes_params: EpisodesParamsDep,
):
    episodes = await service.get_episodes(**episodes_params.model_dump())
    return {"status": "ok", "data": episodes}


@v1_router.get("/{episode_id}")
async def get_episode(
    service: Annotated[EpisodeService, Depends(ServiceFactory.episode_service_factory)],
    episode_id: UUID,
):
    try:
        episode = await service.get_episode(episode_id=episode_id)
    except EpisodeNotFoundException:
        raise EpisodeNotFoundHTTPException
    return {"status": "ok", "data": episode}


@v1_router.post("", dependencies=[AdminDep], status_code=201)
async def add_episode(
    service: Annotated[EpisodeService, Depends(ServiceFactory.episode_service_factory)],
    episode_data: EpisodeAddRequestDTO,
):
    try:
        episode_id = await service.add_episode(episode_data=episode_data)
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
    service: Annotated[EpisodeService, Depends(ServiceFactory.episode_service_factory)],
    episode_id: UUID,
    episode_data: EpisodePatchRequestDTO,
):
    try:
        await service.update_episode(episode_id=episode_id, episode_data=episode_data)
    except EpisodeNotFoundException:
        raise EpisodeNotFoundHTTPException
    except UniqueEpisodePerSeasonException:
        raise UniqueEpisodePerSeasonHTTPException
    except UniqueFileURLException:
        raise UniqueFileURLHTTPException
    return {"status": "ok"}


@v1_router.delete("/{episode_id}", dependencies=[AdminDep], status_code=204)
async def delete_episode(
    service: Annotated[EpisodeService, Depends(ServiceFactory.episode_service_factory)],
    episode_id: UUID,
):
    await service.delete_episode(episode_id=episode_id)
