from typing import List
from urllib.parse import unquote
from uuid import UUID

from fastapi.requests import Request

from src.enums import Qualities, ContentType
from src.exceptions import (
    InvalidContentTypeException,
    ObjectNotFoundException,
    VideoNotFoundException,
    NoExtensionException,
    VideoAlreadyExistsException,
    ExtensionTooLongException,
    UploadFailureException,
    VideoUploadFailedException,
    FileTooLargeException,
    VideoFileTooLargeException,
)
from src.schemas.files import FileAddDTO
from src.services.base import BaseService
from src.tasks.tasks import process_video
from src.services.utils import (
    sanitize_filename,
    validate_video_mime_type,
    get_base_video_storage_key,
    get_original_file_storage_key,
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
        request: Request,
    ):
        if await self.check_video_exists(content_id=content_id):
            raise VideoAlreadyExistsException

        mime_type = request.headers.get("content-type")
        try:
            validate_video_mime_type(mime_type)
            filename = sanitize_filename(unquote(request.headers["filename"]))
        except (
            InvalidContentTypeException,
            NoExtensionException,
            ExtensionTooLongException,
        ):
            raise

        storage_base_key = get_base_video_storage_key(content_id)
        original_file_key = get_original_file_storage_key(storage_base_key, filename)

        try:
            file_size = await self.storage.upload_streaming_file(
                stream=request.stream(),
                key=original_file_key,
            )
        except UploadFailureException:
            raise VideoUploadFailedException
        except FileTooLargeException:
            raise VideoFileTooLargeException

        await self.db.videos.add(
            FileAddDTO(
                content_id=content_id,
                filename=filename,
                storage_path=storage_base_key,
                mime_type=mime_type,
                size_in_bytes=file_size,
                content_type=content_type,
            )
        )

        process_video.delay(
            storage_src_key=original_file_key,
            storage_dst_key=storage_base_key,
            qualities=qualities,
        )

        await self.db.commit()
        return filename

    async def delete_video(self, content_id: UUID):
        video_info = await self.db.videos.get_one_or_none(content_id=content_id)
        if not video_info:
            return
        await self.storage.delete_dir(key=video_info.storage_path)
        await self.db.videos.delete(content_id=video_info.content_id)
        await self.db.commit()
