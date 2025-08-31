from fastapi import APIRouter

from src.api.dependencies import DBDep, PaginationDep
from src.exceptions import (
    LanguageAlreadyExistsException,
    LanguageAlreadyExistsHTTPException,
    LanguageNotFoundException,
    LanguageNotFoundHTTPException,
)
from src.schemas.languages import LanguageAddRequestDTO
from src.services.languages import LanguageService


v1_router = APIRouter(prefix="/v1/languages", tags=["languages"])


@v1_router.get("")
async def get_languages(db: DBDep, pagination: PaginationDep):
    langs = await LanguageService(db).get_languages(
        page=pagination.page,
        per_page=pagination.per_page,
    )
    return {"status": "ok", "data": langs}


@v1_router.get("/{lang_id}")
async def get_language(db: DBDep, lang_id: int):
    try:
        lang = await LanguageService(db).get_language(lang_id)
    except LanguageNotFoundException:
        raise LanguageNotFoundHTTPException
    return {"status": "ok", "data": lang}


@v1_router.post("", status_code=201)
async def add_language(db: DBDep, lang_data: LanguageAddRequestDTO):
    try:
        lang_id = await LanguageService(db).add_language(lang_data)
    except LanguageAlreadyExistsException:
        raise LanguageAlreadyExistsHTTPException
    return {"status": "ok", "data": {"id": lang_id}}


@v1_router.delete("/{lang_id}", status_code=204)
async def delete_language(db: DBDep, lang_id: int):
    await LanguageService(db).delete_language(lang_id)
