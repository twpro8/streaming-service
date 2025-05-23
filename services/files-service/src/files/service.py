from typing import List
from uuid import UUID

from fastapi import UploadFile

from src.core.base.service import BaseService
from src.core.enums import Qualities
from src.tasks.tasks import process_video_and_upload_to_s3, upload_file_to_s3
from src.files.utils import save_to_temp_file, sanitize_filename


class FileService(BaseService):
    @staticmethod
    async def upload_video(content_id: UUID, qualities: List[Qualities], file: UploadFile):
        temp_file_path = save_to_temp_file(file)

        process_video_and_upload_to_s3.delay(
            input_file_path=temp_file_path,
            s3_key=f"videos/{content_id}",
            qualities=qualities,
        )

    @staticmethod
    async def upload_image(content_id: UUID, file: UploadFile):
        temp_file_path = save_to_temp_file(file)

        filename = sanitize_filename(file.filename)

        upload_file_to_s3.delay(
            input_file_path=temp_file_path,
            s3_key=f"images/{content_id}/{filename}",
        )
