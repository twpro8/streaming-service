from typing import List

from fastapi import APIRouter, UploadFile, File, Query

from src.core.enums import ContentType, Qualities
from src.files.service import FileService


router = APIRouter(tags=["Files"])


@router.post("/films/{film_id}/videos")
async def upload_film(
        film_id: int,
        qualities: List[Qualities] = Query(default=[Qualities.CD]),
        file: UploadFile = File(...)
):
    await FileService().upload_film(
        film_id=film_id,
        qualities=qualities,
        file=file
    )
    return {"status": "ok"}


@router.post("/series/{series_id}/videos")
async def upload_episode(
        series_id: int,
        episode_number: int,
        qualities: List[Qualities] = Query(default=[Qualities.CD]),
        file: UploadFile = File(...)
):
    await FileService().upload_episode(
        series_id=series_id,
        episode_number=episode_number,
        qualities=qualities,
        file=file
    )
    return {"status": "ok"}


@router.post("/images")
async def upload_image(
        content_id: int,
        content_type: ContentType,
        file: UploadFile = File(...)
):
    await FileService().upload_image(
        content_id=content_id,
        content_type=content_type,
        file=file
    )
    return {"status": "ok"}
