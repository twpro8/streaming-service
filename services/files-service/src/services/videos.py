from typing import List
from uuid import UUID

from fastapi import UploadFile

from src.enums import Qualities, ContentType
from src.exceptions import (
    InvalidContentTypeException,
    ObjectNotFoundException,
    VideoNotFoundException,
    NoExtensionException,
    ObjectAlreadyExistsException,
    VideoAlreadyExistsException,
    ExtensionTooLongException,
    UploadFailureException,
    VideoUploadFailedException,
)
from src.schemas.files import FileAddDTO
from src.services.base import BaseService
from src.tasks.tasks import process_video
from src.services.utils import (
    sanitize_filename,
    validate_video_mime_type,
    get_video_storage_base_key,
    get_original_file_key,
)


class VideoService(BaseService):
    async def get_videos_info_list(self, pagination):
        return await self.db.videos.get_filtered(page=pagination.page, per_page=pagination.per_page)

    async def get_video_info(self, uuid: UUID):
        try:
            video_info = await self.db.videos.get_one(content_id=uuid)
        except ObjectNotFoundException:
            raise VideoNotFoundException
        return video_info

    async def handle_video_upload(
        self,
        content_id: UUID,
        content_type: ContentType,
        qualities: List[Qualities],
        file: UploadFile,
    ):
        try:
            validate_video_mime_type(file.content_type)
            file.filename = sanitize_filename(file.filename)
        except (
            InvalidContentTypeException,
            NoExtensionException,
            ExtensionTooLongException,
        ):
            raise

        storage_base_key = get_video_storage_base_key(content_id)
        original_file_key = get_original_file_key(storage_base_key, file.filename)

        file_data = await file.read()
        file_size = file.size or len(file_data)

        try:
            await self.db.videos.add(
                FileAddDTO(
                    content_id=content_id,
                    filename=file.filename,
                    storage_path=storage_base_key,
                    mime_type=file.content_type,
                    size_in_bytes=file_size,
                    content_type=content_type,
                )
            )
        except ObjectAlreadyExistsException:
            raise VideoAlreadyExistsException

        try:
            await self.storage.upload_file(
                key=original_file_key,
                data=file_data,
            )
        except UploadFailureException:
            raise VideoUploadFailedException

        await self.db.commit()

        process_video.delay(
            storage_src_key=original_file_key,
            storage_dst_key=storage_base_key,
            qualities=qualities,
        )

    async def delete_video(self, content_id: UUID):
        video_info = await self.db.videos.get_one_or_none(content_id=content_id)
        if not video_info:
            return
        await self.storage.delete_dir(key=video_info.storage_path)
        await self.db.videos.delete(content_id=video_info.content_id)
        await self.db.commit()
