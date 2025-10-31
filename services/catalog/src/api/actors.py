from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends

from src.api.dependencies import PaginationDep, AdminDep
from src.factories.service import ServiceFactory
from src.schemas.actors import ActorAddRequestDTO, ActorPatchDTO
from src.services.actors import ActorService


v1_router = APIRouter(prefix="/v1/actors", tags=["Actors"])


@v1_router.get("")
async def get_actors(
    service: Annotated[ActorService, Depends(ServiceFactory.actor_service_factory)],
    pagination: PaginationDep,
):
    actors = await service.get_actors(
        page=pagination.page,
        per_page=pagination.per_page,
    )
    return {"status": "ok", "data": actors}


@v1_router.get("/{actor_id}")
async def get_actor(
    service: Annotated[ActorService, Depends(ServiceFactory.actor_service_factory)],
    actor_id: UUID,
):
    actor = await service.get_actor(actor_id=actor_id)
    return {"status": "ok", "data": actor}


@v1_router.post("", dependencies=[AdminDep], status_code=201)
async def add_actor(
    service: Annotated[ActorService, Depends(ServiceFactory.actor_service_factory)],
    actor_data: ActorAddRequestDTO,
):
    actor_id = await service.add_actor(actor_data=actor_data)
    return {"status": "ok", "data": {"id": actor_id}}


@v1_router.patch("/{actor_id}", dependencies=[AdminDep])
async def update_actor(
    service: Annotated[ActorService, Depends(ServiceFactory.actor_service_factory)],
    actor_id: UUID,
    actor_data: ActorPatchDTO,
):
    await service.update_actor(actor_id=actor_id, actor_data=actor_data)
    return {"status": "ok"}


@v1_router.delete("/{actor_id}", status_code=204, dependencies=[AdminDep])
async def delete_actor(
    service: Annotated[ActorService, Depends(ServiceFactory.actor_service_factory)],
    actor_id: UUID,
):
    await service.delete_actor(actor_id=actor_id)
