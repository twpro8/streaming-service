from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from src.factories.service import ServiceFactory
from src.services.episodes import EpisodeService
from src.api.dependencies import AdminDep, PaginationDep
from src.schemas.episodes import EpisodePatchRequestDTO, EpisodeAddRequestDTO


v1_router = APIRouter(prefix="/v1/episodes", tags=["Episodes"])


@v1_router.get("", summary="Get episodes")
async def get_episodes(
    service: Annotated[EpisodeService, Depends(ServiceFactory.episode_service_factory)],
    pagination: PaginationDep,
    show_id: Annotated[UUID | None, Query()] = None,
    season_id: Annotated[UUID | None, Query()] = None,
    episode_number: Annotated[int | None, Query(ge=1, le=9999)] = None,
):
    episodes = await service.get_episodes(
        show_id=show_id,
        season_id=season_id,
        episode_number=episode_number,
        page=pagination.page,
        per_page=pagination.per_page,
    )
    return {"status": "ok", "data": episodes}


@v1_router.get("/{episode_id}")
async def get_episode(
    service: Annotated[EpisodeService, Depends(ServiceFactory.episode_service_factory)],
    episode_id: UUID,
):
    episode = await service.get_episode(episode_id=episode_id)
    return {"status": "ok", "data": episode}


@v1_router.post("", dependencies=[AdminDep], status_code=201)
async def add_episode(
    service: Annotated[EpisodeService, Depends(ServiceFactory.episode_service_factory)],
    episode_data: EpisodeAddRequestDTO,
):
    episode_id = await service.add_episode(episode_data=episode_data)
    return {"status": "ok", "data": {"id": episode_id}}


@v1_router.patch("/{episode_id}", dependencies=[AdminDep])
async def update_episode(
    service: Annotated[EpisodeService, Depends(ServiceFactory.episode_service_factory)],
    episode_id: UUID,
    episode_data: EpisodePatchRequestDTO,
):
    await service.update_episode(episode_id=episode_id, episode_data=episode_data)
    return {"status": "ok"}


@v1_router.delete("/{episode_id}", dependencies=[AdminDep], status_code=204)
async def delete_episode(
    service: Annotated[EpisodeService, Depends(ServiceFactory.episode_service_factory)],
    episode_id: UUID,
):
    await service.delete_episode(episode_id=episode_id)
