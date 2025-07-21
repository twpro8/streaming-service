from typing import List
from uuid import UUID

from fastapi import APIRouter, UploadFile, File, Query

from src.enums import Qualities, ContentType
from src.exceptions import (
    InvalidContentTypeException,
    InvalidVideoTypeHTTPException,
    VideoNotFoundException,
    VideoNotFoundHTTPException,
    NoExtensionException,
    NoExtensionHTTPException,
    VideoAlreadyExistsException,
    VideoAlreadyExistsHTTPException,
    ExtensionTooLongException,
    ExtensionTooLongHTTPException,
    VideoUploadFailedException,
    VideoUploadFailedHTTPException,
)
from src.api.dependencies import VideoServiceDep, PaginationDep


router = APIRouter(prefix="/videos", tags=["Videos"])


@router.get("")
async def get_videos_info_list(video_service: VideoServiceDep, pagination: PaginationDep):
    video_info_list = await video_service.get_videos_info_list(pagination)
    return {"status": "ok", "data": video_info_list}


@router.get("/{content_id}")
async def get_video_info(video_service: VideoServiceDep, content_id: UUID):
    try:
        video_info = await video_service.get_video_info(content_id)
    except VideoNotFoundException:
        raise VideoNotFoundHTTPException
    return {"status": "ok", "data": video_info}


@router.post("/{content_id}")
async def upload_video(
    video_service: VideoServiceDep,
    content_id: UUID,
    content_type: ContentType,
    qualities: List[Qualities] = Query(default=[Qualities.CD]),
    file: UploadFile = File(...),
):
    try:
        await video_service.handle_video_upload(
            content_id=content_id,
            content_type=content_type,
            qualities=qualities,
            file=file,
        )
    except InvalidContentTypeException:
        raise InvalidVideoTypeHTTPException
    except NoExtensionException:
        raise NoExtensionHTTPException
    except ExtensionTooLongException:
        raise ExtensionTooLongHTTPException
    except VideoAlreadyExistsException:
        raise VideoAlreadyExistsHTTPException
    except VideoUploadFailedException:
        raise VideoUploadFailedHTTPException
    return {"status": "ok"}


@router.delete("/files/{content_id}", status_code=204)
async def delete_video(
    video_service: VideoServiceDep,
    content_id: UUID,
):
    await video_service.delete_video(content_id=content_id)
