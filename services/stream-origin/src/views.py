from uuid import UUID

from fastapi import APIRouter
from fastapi.responses import Response, RedirectResponse
from fastapi.exceptions import HTTPException

from src import s3_client
from src.enums import Quality


router = APIRouter(prefix="/videos", tags=["Stream"])


@router.get("/{video_id}/master.m3u8")
async def get_master_playlist(video_id: UUID):
    key = f"videos/{video_id}/master.m3u8"
    try:
        content = await s3_client.get_file(key)
        return Response(content=content, media_type="application/vnd.apple.mpegurl")
    except Exception:
        raise HTTPException(status_code=404, detail="Master playlist not found")


@router.get("/{video_id}/{quality}/index.m3u8")
async def get_index_playlist(video_id: UUID, quality: Quality):
    key = f"videos/{video_id}/{quality}/index.m3u8"
    try:
        content = await s3_client.get_file(key)
    except Exception:
        raise HTTPException(status_code=404, detail="index.m3u8 not found")

    return Response(content=content, media_type="application/vnd.apple.mpegurl")


@router.get("/{video_id}/{quality}/{segment_name}")
async def get_segment(video_id: UUID, quality: Quality, segment_name: str):
    key = f"videos/{video_id}/{quality}/{segment_name}"
    url = await s3_client.generate_presigned_url(key, expires=600)

    if not url:
        raise HTTPException(status_code=404, detail="Segment not found")

    return RedirectResponse(url, status_code=307)
