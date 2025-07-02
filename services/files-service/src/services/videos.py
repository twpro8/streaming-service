from typing import List
from uuid import UUID

from fastapi import UploadFile

from src.config import settings
from src.enums import Qualities, ContentType
from src.exceptions import (
    InvalidContentTypeException,
    ObjectNotFoundException,
    VideoNotFoundException,
)
from src.schemas.files import FileAddDTO
from src.services.base import BaseService
from src.tasks.tasks import process_video_and_upload_to_s3
from src.services.utils import save_to_temp_file, sanitize_filename


class VideoService(BaseService):
    async def get_videos_info_list(self, pagination):
        return await self.db.videos.get_filtered(page=pagination.page, per_page=pagination.per_page)

    async def get_video_info(self, uuid: UUID):
        try:
            video_info = await self.db.videos.get_one(content_id=uuid)
        except ObjectNotFoundException:
            raise VideoNotFoundException
        return video_info

    async def upload_video(
        self,
        content_id: UUID,
        content_type: ContentType,
        qualities: List[Qualities],
        file: UploadFile,
    ):
        if file.content_type not in settings.INPUT_VIDEO_MIMO:
            raise InvalidContentTypeException

        storage_path = f"videos/{content_id}"
        original_filename = sanitize_filename(file.filename)

        await self.db.videos.add(
            FileAddDTO(
                content_id=content_id,
                filename=original_filename,
                storage_path=storage_path,
                mime_type="application/vnd.apple.mpegurl",
                size_in_bytes=file.size,
                content_type=ContentType(content_type),
            )
        )

        temp_file_path = save_to_temp_file(file)

        process_video_and_upload_to_s3.delay(
            input_file_path=temp_file_path,
            s3_key=storage_path,
            qualities=qualities,
        )
        await self.db.commit()

    async def delete_video(self, content_id: UUID):
        video_info = await self.db.videos.get_one_or_none(content_id=content_id)
        if not video_info:
            return
        await self.storage.delete_dir(key=video_info.storage_path)
        await self.db.videos.delete(content_id=video_info.content_id)
        await self.db.commit()
