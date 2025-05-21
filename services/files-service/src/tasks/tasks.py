import logging
import os
from typing import List
import asyncio
from tempfile import TemporaryDirectory
from pathlib import Path

from src import s3_client
from src.core.enums import Qualities
from src.tasks.celery_app import celery_instance
from src.tasks.utils import update_master_playlist_from_s3
from src.video.transcoder import HlsTranscoder, BITRATE_SETTINGS

log = logging.getLogger(__name__)


@celery_instance.task
def process_video_and_upload_to_s3(
    input_file_path: str,
    s3_key: str,
    qualities: List[Qualities],
):
    with TemporaryDirectory() as tmp:
        temp_dir = Path(tmp)

        HlsTranscoder(
            input_path=input_file_path, output_dir=temp_dir, qualities=qualities
        ).transcode()

        for quality_dir in temp_dir.iterdir():
            if not quality_dir.is_dir():
                continue

            # delete old files for exact resolution if any
            asyncio.run(s3_client.delete_bulk(f"{s3_key}/{quality_dir.name}"))

            for file in quality_dir.iterdir():
                if file.is_file():
                    key = f"{s3_key}/{quality_dir.name}/{file.name}"
                    upload_file_to_s3(file, key)

        asyncio.run(update_master_playlist_from_s3(s3_key=s3_key, input_path=input_file_path))

    # clear tmp uploaded video file
    os.remove(input_file_path)


@celery_instance.task
def upload_file_to_s3(
    input_file_path: str,
    s3_key: str,
):
    with open(input_file_path, "rb") as f:
        data = f.read()

    success = asyncio.run(s3_client.upload_file(s3_key, data))
    if success:
        log.info(f"Uploaded {s3_key}")
    else:
        log.error(f"Failed to upload {s3_key}")

    os.remove(input_file_path)
