from uuid import UUID

from src.enums import Quality
from src.exceptions import (
    ObjectNotFoundException,
    PlaylistNotFoundException,
    SegmentNotFoundException,
)
from src.services.base import BaseService


class VideoService(BaseService):
    async def get_master_playlist(self, video_id: UUID):
        key = f"videos/{video_id}/master.m3u8"
        try:
            playlist = await self.storage.get_file(key)
        except ObjectNotFoundException:
            raise PlaylistNotFoundException
        return playlist

    async def get_index_playlist(self, video_id: UUID, quality: Quality):
        key = f"videos/{video_id}/{quality}/index.m3u8"
        try:
            playlist = await self.storage.get_file(key)
        except ObjectNotFoundException:
            raise PlaylistNotFoundException
        return playlist

    async def get_segment(self, video_id: UUID, quality: Quality, segment_name: str):
        key = f"videos/{video_id}/{quality}/{segment_name}"
        try:
            segment = await self.storage.get_file(key)
        except ObjectNotFoundException:
            raise SegmentNotFoundException
        return segment

    async def get_segment_url(self, video_id: UUID, quality: Quality, segment_name: str):
        key = f"videos/{video_id}/{quality}/{segment_name}"
        url = await self.storage.generate_presigned_url(key, expires=600)
        return url
