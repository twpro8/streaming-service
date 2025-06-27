from typing import List
from uuid import UUID

from fastapi import UploadFile

from src.config import settings
from src.core.base.service import BaseService
from src.core.enums import Qualities, VideoType, ContentType
from src.exceptions import InvalidContentTypeException
from src.files.schemas import FileAddDTO
from src.tasks.tasks import process_video_and_upload_to_s3, upload_file_to_s3
from src.files.utils import save_to_temp_file, sanitize_filename


class FileService(BaseService):
    async def upload_video(
        self,
        content_id: UUID,
        video_type: VideoType,
        qualities: List[Qualities],
        file: UploadFile,
    ):
        if file.content_type not in settings.INPUT_VIDEO_MIMO:
            raise InvalidContentTypeException

        s3_key = f"videos/{content_id}"
        filename = sanitize_filename(file.filename)

        await self.db.files.add(
            FileAddDTO(
                content_id=content_id,
                filename=filename,
                s3_key=s3_key,
                mime_type="application/vnd.apple.mpegurl",
                size=file.size,
                content_type=ContentType(video_type),
            )
        )

        temp_file_path = save_to_temp_file(file)

        process_video_and_upload_to_s3.delay(
            input_file_path=temp_file_path,
            s3_key=s3_key,
            qualities=qualities,
        )
        await self.db.commit()

    async def upload_image(self, content_id: UUID, file: UploadFile):
        if file.content_type not in ("image/jpeg", "image/jpg", "image/png"):
            raise InvalidContentTypeException

        filename = sanitize_filename(file.filename)
        s3_key = f"images/{content_id}.{file.content_type.split('/')[-1]}"

        await self.db.files.add(
            FileAddDTO(
                content_id=content_id,
                filename=filename,
                s3_key=s3_key,
                mime_type=file.content_type,
                size=file.size,
                content_type=ContentType.image,
            )
        )

        temp_file_path = save_to_temp_file(file)

        upload_file_to_s3.delay(input_file_path=temp_file_path, s3_key=s3_key)
        await self.db.commit()

    async def delete_file(self, content_id: UUID, content_type: ContentType):
        file = await self.db.files.get_one_or_none(content_id=content_id, content_type=content_type)
        if not file:
            return
        await self.storage.delete_dir(key=file.s3_key)
        await self.db.files.delete(id=file.id)
        await self.db.commit()
