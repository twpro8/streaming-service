from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Query, Depends

from src.factories.service import ServiceFactory
from src.schemas.shows import ShowAddRequestDTO, ShowPatchRequestDTO
from src.services.shows import ShowService
from src.api.dependencies import AdminDep, ContentParamsDep, SortDep


v1_router = APIRouter(prefix="/v1/shows", tags=["Shows"])


@v1_router.get("")
async def get_shows(
    service: Annotated[ShowService, Depends(ServiceFactory.show_service_factory)],
    common_params: ContentParamsDep,
    sort: SortDep,
    directors_ids: Annotated[List[UUID] | None, Query()] = None,
    actors_ids: Annotated[List[UUID] | None, Query()] = None,
    genres_ids: Annotated[List[int] | None, Query()] = None,
    countries_ids: Annotated[List[int] | None, Query()] = None,
):
    shows = await service.get_shows(
        directors_ids=directors_ids,
        actors_ids=actors_ids,
        genres_ids=genres_ids,
        countries_ids=countries_ids,
        sort_by=sort.field,
        sort_order=sort.order,
        **common_params.model_dump(),
    )
    return {"status": "ok", "data": shows}


@v1_router.get("/{show_id}")
async def get_show(
    service: Annotated[ShowService, Depends(ServiceFactory.show_service_factory)],
    show_id: UUID,
):
    show = await service.get_show(show_id=show_id)
    return {"status": "ok", "data": show}


@v1_router.post("", dependencies=[AdminDep], status_code=201)
async def add_show(
    service: Annotated[ShowService, Depends(ServiceFactory.show_service_factory)],
    show_data: ShowAddRequestDTO,
):
    show_id = await service.add_show(show_data=show_data)
    return {"status": "ok", "data": {"id": show_id}}


@v1_router.patch("/{show_id}", dependencies=[AdminDep])
async def update_show(
    service: Annotated[ShowService, Depends(ServiceFactory.show_service_factory)],
    show_id: UUID,
    show_data: ShowPatchRequestDTO,
):
    await service.update_show(show_id=show_id, show_data=show_data)
    return {"status": "ok"}


@v1_router.delete("/{show_id}", dependencies=[AdminDep], status_code=204)
async def delete_show(
    service: Annotated[ShowService, Depends(ServiceFactory.show_service_factory)],
    show_id: UUID,
):
    await service.delete_show(show_id=show_id)
