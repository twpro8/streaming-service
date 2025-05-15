import shutil
from tempfile import NamedTemporaryFile
from typing import List

from fastapi import UploadFile

from src import s3_client
from src.core.base.service import BaseService
from src.core.enums import Qualities, ContentType
from src.tasks.tasks import process_video_and_upload_to_s3, upload_file_to_s3


class FileService(BaseService):
    async def upload_film(
        self,
        film_id: int,
        qualities: List[Qualities],
        file: UploadFile
    ):
        with NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
            shutil.copyfileobj(file.file, tmp)
            temp_file_path = tmp.name

        s3_key = f"films/{film_id}"
        process_video_and_upload_to_s3.delay(
            input_file_path=temp_file_path,
            s3_key=s3_key,
            qualities=qualities,
        )

    async def upload_episode(
        self,
        series_id: int,
        episode_number: int,
        qualities: List[Qualities],
        file: UploadFile
    ):
        with NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
            shutil.copyfileobj(file.file, tmp)
            temp_file_path = tmp.name

        s3_key = f"series/{series_id}/episodes/{episode_number}"
        process_video_and_upload_to_s3.delay(
            input_file_path=temp_file_path,
            s3_key=s3_key,
            qualities=qualities,
        )

    async def upload_image(
        self,
        content_id: int,
        content_type: ContentType,
        file: UploadFile
    ):
        with NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
            shutil.copyfileobj(file.file, tmp)
            temp_file_path = tmp.name

        filename = s3_client.sanitize_filename(file.filename)

        s3_key = f"{content_type}/{content_id}/covers/{filename}"
        upload_file_to_s3.delay(
            input_file_path=temp_file_path,
            s3_key=s3_key,
        )
