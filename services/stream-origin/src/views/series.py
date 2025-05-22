from fastapi import APIRouter
from fastapi.responses import Response, RedirectResponse
from fastapi.exceptions import HTTPException

from src import s3_client
from src.enums import Quality


router = APIRouter(prefix="/series", tags=["Series"])


@router.get("/{series_id}/episodes/{episode_number}/master.m3u8")
async def get_master_playlist(series_id: str, episode_number: int):
    key = f"series/{series_id}/episodes/{episode_number}/master.m3u8"
    try:
        content = await s3_client.get_file(key)
        return Response(content=content, media_type="application/vnd.apple.mpegurl")
    except Exception:
        raise HTTPException(status_code=404, detail="Master playlist not found")


@router.get("/{series_id}/episodes/{episode_number}/{quality}/index.m3u8")
async def get_index_playlist(series_id: str, episode_number: int, quality: Quality):
    key = f"series/{series_id}/episodes/{episode_number}/{quality}/index.m3u8"
    try:
        content = await s3_client.get_file(key)
    except Exception:
        raise HTTPException(status_code=404, detail="index.m3u8 not found")

    return Response(content=content, media_type="application/vnd.apple.mpegurl")


@router.get("/{series_id}/episodes/{episode_number}/{quality}/{segment_name}")
async def get_segment(series_id: str, episode_number: int, quality: Quality, segment_name: str):
    key = f"series/{series_id}/episodes/{episode_number}/{quality}/{segment_name}"
    url = await s3_client.generate_presigned_url(key, expires=600)

    if not url:
        raise HTTPException(status_code=404, detail="Segment not found")

    return RedirectResponse(url, status_code=307)
