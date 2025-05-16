from typing import List

from fastapi import UploadFile

from src.core.base.service import BaseService
from src.core.enums import Qualities, ContentType
from src.tasks.tasks import process_video_and_upload_to_s3, upload_file_to_s3
from src.files.utils import (
    save_to_temp_file,
    generate_film_s3_key,
    generate_episode_s3_key,
    generate_image_s3_key,
    sanitize_filename,
)


class FileService(BaseService):
    async def upload_film(self, film_id: int, qualities: List[Qualities], file: UploadFile):
        temp_file_path = save_to_temp_file(file)

        s3_key = generate_film_s3_key(film_id)
        process_video_and_upload_to_s3.delay(
            input_file_path=temp_file_path,
            s3_key=s3_key,
            qualities=qualities,
        )

    async def upload_episode(
        self, series_id: int, episode_number: int, qualities: List[Qualities], file: UploadFile
    ):
        temp_file_path = save_to_temp_file(file)

        s3_key = generate_episode_s3_key(series_id, episode_number)
        process_video_and_upload_to_s3.delay(
            input_file_path=temp_file_path,
            s3_key=s3_key,
            qualities=qualities,
        )

    async def upload_image(self, content_id: int, content_type: ContentType, file: UploadFile):
        temp_file_path = save_to_temp_file(file)

        filename = sanitize_filename(file.filename)

        s3_key = generate_image_s3_key(content_type, content_id, filename)
        upload_file_to_s3.delay(
            input_file_path=temp_file_path,
            s3_key=s3_key,
        )
