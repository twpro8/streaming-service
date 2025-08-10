from uuid import UUID

from fastapi import APIRouter

from src.api.dependencies import DBDep, PaginationDep, AdminDep
from src.exceptions import (
    ActorAlreadyExistsException,
    ActorAlreadyExistsHTTPException,
    ActorNotFoundException,
    ActorNotFoundHTTPException,
)
from src.schemas.actors import ActorAddDTO, ActorPatchDTO
from src.services.actors import ActorService


router = APIRouter(prefix="/actors", tags=["Actors"])


@router.get("", status_code=201)
async def get_actors(db: DBDep, pagination: PaginationDep):
    actors = await ActorService(db).get_actors(
        page=pagination.page,
        per_page=pagination.per_page,
    )
    return {"status": "ok", "data": actors}


@router.get("/{actor_id}")
async def get_actor(db: DBDep, actor_id: UUID):
    try:
        actor = await ActorService(db).get_actor(actor_id=actor_id)
    except ActorNotFoundException:
        raise ActorNotFoundHTTPException
    return {"status": "ok", "data": actor}


@router.post("", dependencies=[AdminDep])
async def add_actor(db: DBDep, actor_data: ActorAddDTO):
    try:
        actor = await ActorService(db).add_actor(actor_data=actor_data)
    except ActorAlreadyExistsException:
        raise ActorAlreadyExistsHTTPException
    return {"status": "ok", "data": actor}


@router.patch("/{actor_id}", dependencies=[AdminDep])
async def update_actor(db: DBDep, actor_id: UUID, actor_data: ActorPatchDTO):
    try:
        await ActorService(db).update_actor(actor_id=actor_id, actor_data=actor_data)
    except ActorAlreadyExistsException:
        raise ActorAlreadyExistsHTTPException
    return {"status": "ok"}


@router.delete("/{actor_id}", status_code=204, dependencies=[AdminDep])
async def delete_actor(db: DBDep, actor_id: UUID):
    await ActorService(db).delete_actor(actor_id=actor_id)
