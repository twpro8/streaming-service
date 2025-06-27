from uuid import UUID

from fastapi import APIRouter
from fastapi.responses import Response

from src.enums import Quality
from src.exceptions import (
    PlaylistNotFoundException,
    PlaylistNotFoundHTTPException,
    SegmentNotFoundException,
    SegmentNotFoundHTTPException,
)
from src.api.dependencies import VideoServiceDep


router = APIRouter(prefix="/videos", tags=["Stream"])


@router.get("/{video_id}/master.m3u8")
async def get_master_playlist(video_service: VideoServiceDep, video_id: UUID):
    try:
        playlist = await video_service.get_master_playlist(video_id)
    except PlaylistNotFoundException:
        raise PlaylistNotFoundHTTPException
    return Response(content=playlist, media_type="application/vnd.apple.mpegurl")


@router.get("/{video_id}/{quality}/index.m3u8")
async def get_index_playlist(video_service: VideoServiceDep, video_id: UUID, quality: Quality):
    try:
        playlist = await video_service.get_index_playlist(video_id, quality)
    except PlaylistNotFoundException:
        raise PlaylistNotFoundHTTPException
    return Response(content=playlist, media_type="application/vnd.apple.mpegurl")


@router.get("/{video_id}/{quality}/{segment_name}")
async def get_segment(
    video_service: VideoServiceDep, video_id: UUID, quality: Quality, segment_name: str
):
    try:
        segment = await video_service.get_segment(video_id, quality, segment_name)
    except SegmentNotFoundException:
        raise SegmentNotFoundHTTPException
    return Response(content=segment, media_type="application/vnd.apple.mpegurl")
