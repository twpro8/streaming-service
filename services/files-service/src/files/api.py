from typing import List
from uuid import UUID

from fastapi import APIRouter, UploadFile, File, Query

from src.core.enums import Qualities, VideoType, ContentType
from src.exceptions import (
    InvalidContentTypeException,
    InvalidVideoTypeHTTPException,
    InvalidImageTypeHTTPException,
)
from src.files.dependencies import FileServiceDep


router = APIRouter(tags=["Files"])


@router.post("/videos/{content_id}")
async def upload_video(
    file_service: FileServiceDep,
    content_id: UUID,
    video_type: VideoType,
    qualities: List[Qualities] = Query(default=[Qualities.CD]),
    file: UploadFile = File(...),
):
    try:
        await file_service.upload_video(
            content_id=content_id,
            video_type=video_type,
            qualities=qualities,
            file=file,
        )
    except InvalidContentTypeException:
        raise InvalidVideoTypeHTTPException
    return {"status": "ok"}


@router.post("/images/{content_id}")
async def upload_image(
    file_service: FileServiceDep, content_id: UUID, file: UploadFile = File(...)
):
    try:
        await file_service.upload_image(content_id=content_id, file=file)
    except InvalidContentTypeException:
        raise InvalidImageTypeHTTPException
    return {"status": "ok"}


@router.delete("/files/{content_id}", status_code=204)
async def delete_file(
    file_service: FileServiceDep, content_id: UUID, content_type: ContentType = Query(...)
):
    await file_service.delete_file(content_id=content_id, content_type=content_type)
