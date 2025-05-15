import logging
import os
from typing import List
import asyncio
from tempfile import TemporaryDirectory
from pathlib import Path

from src import s3_client
from src.core.enums import Qualities
from src.tasks.celery_app import celery_instance
from src.tasks.utils import transcode_to_hls


log = logging.getLogger(__name__)


@celery_instance.task
def process_video_and_upload_to_s3(
    input_file_path: str,
    s3_key: int,
    qualities: List[Qualities],
):
    with TemporaryDirectory() as tmp:
        temp_dir = Path(tmp)

        transcode_to_hls(input_path=input_file_path, output_dir=temp_dir, qualities=qualities)

        for quality_dir in temp_dir.iterdir():
            if not quality_dir.is_dir():
                continue

            # delete old files for exact resolution if any
            asyncio.run(s3_client.delete_bulk(f"{s3_key}/{quality_dir.name}"))

            for file in quality_dir.iterdir():
                if file.is_file():
                    key = f"{s3_key}/{quality_dir.name}/{file.name}"

                    with open(file, "rb") as f:
                        data = f.read()

                    success = asyncio.run(s3_client.upload_file(key, data))
                    if success:
                        log.info(f"Uploaded {s3_key}")
                    else:
                        log.error(f"Failed to upload {s3_key}")

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
