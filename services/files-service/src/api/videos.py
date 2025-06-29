from typing import List
from uuid import UUID

from fastapi import APIRouter, UploadFile, File, Query

from src.enums import Qualities, ContentType
from src.exceptions import (
    InvalidContentTypeException,
    InvalidVideoTypeHTTPException,
)
from src.api.dependencies import VideoServiceDep


router = APIRouter(prefix="/videos", tags=["Videos"])


@router.post("/{content_id}")
async def upload_video(
    video_service: VideoServiceDep,
    content_id: UUID,
    content_type: ContentType,
    qualities: List[Qualities] = Query(default=[Qualities.CD]),
    file: UploadFile = File(...),
):
    try:
        await video_service.upload_video(
            content_id=content_id,
            content_type=content_type,
            qualities=qualities,
            file=file,
        )
    except InvalidContentTypeException:
        raise InvalidVideoTypeHTTPException
    return {"status": "ok"}


@router.delete("/files/{content_id}", status_code=204)
async def delete_video(
    video_service: VideoServiceDep,
    content_id: UUID,
):
    await video_service.delete_video(content_id=content_id)
