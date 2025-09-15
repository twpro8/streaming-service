from typing import Annotated

from fastapi import APIRouter, Depends

from src.api.dependencies import PaginationDep, AdminDep
from src.exceptions import (
    LanguageAlreadyExistsException,
    LanguageAlreadyExistsHTTPException,
    LanguageNotFoundException,
    LanguageNotFoundHTTPException,
)
from src.factories.service import ServiceFactory
from src.schemas.languages import LanguageAddRequestDTO
from src.services.languages import LanguageService


v1_router = APIRouter(prefix="/v1/languages", tags=["languages"])


@v1_router.get("")
async def get_languages(
    service: Annotated[LanguageService, Depends(ServiceFactory.language_service_factory)],
    pagination: PaginationDep,
):
    langs = await service.get_languages(
        page=pagination.page,
        per_page=pagination.per_page,
    )
    return {"status": "ok", "data": langs}


@v1_router.get("/{lang_id}")
async def get_language(
    service: Annotated[LanguageService, Depends(ServiceFactory.language_service_factory)],
    lang_id: int,
):
    try:
        lang = await service.get_language(lang_id=lang_id)
    except LanguageNotFoundException:
        raise LanguageNotFoundHTTPException
    return {"status": "ok", "data": lang}


@v1_router.post("", dependencies=[AdminDep], status_code=201)
async def add_language(
    service: Annotated[LanguageService, Depends(ServiceFactory.language_service_factory)],
    lang_data: LanguageAddRequestDTO,
):
    try:
        lang_id = await service.add_language(lang_data=lang_data)
    except LanguageAlreadyExistsException:
        raise LanguageAlreadyExistsHTTPException
    return {"status": "ok", "data": {"id": lang_id}}


@v1_router.delete("/{lang_id}", dependencies=[AdminDep], status_code=204)
async def delete_language(
    service: Annotated[LanguageService, Depends(ServiceFactory.language_service_factory)],
    lang_id: int,
):
    await service.delete_language(lang_id=lang_id)
