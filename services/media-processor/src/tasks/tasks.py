import logging
import os
import tempfile
from typing import List
import asyncio
from tempfile import TemporaryDirectory
from pathlib import Path

from src.exceptions import UploadFailureException
from src.factories.storage_adapter_factories import StorageAdapterFactory
from src.enums import Qualities
from src.tasks.celery_app import celery_instance
from src.tasks.utils import update_master_playlist_from_s3
from src.utils.transcoder import HlsTranscoder


log = logging.getLogger(__name__)
storage = StorageAdapterFactory.s3_adapter_sync_factory()


@celery_instance.task
def process_video(
    storage_src_key: str,
    storage_dst_key: str,
    qualities: List[Qualities],
):
    video = asyncio.run(storage.get_file(storage_src_key))
    log.info(f"Downloaded video {storage_src_key}")

    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(video)
        input_file_path = temp_file.name

    with TemporaryDirectory() as tmp:
        temp_dir = Path(tmp)

        HlsTranscoder(
            input_path=input_file_path,
            output_dir=temp_dir,
            qualities=qualities,
        ).transcode()

        for quality_dir in temp_dir.iterdir():
            if not quality_dir.is_dir():
                continue

            # delete old files for exact resolution if any
            asyncio.run(storage.delete_dir(f"{storage_dst_key}/{quality_dir.name}"))

            for file in quality_dir.iterdir():
                if file.is_file():
                    key = f"{storage_dst_key}/{quality_dir.name}/{file.name}"
                    upload_file_to_storage(input_file_path=str(file), s3_key=key)

        asyncio.run(
            update_master_playlist_from_s3(
                s3_key=storage_dst_key,
                input_path=input_file_path,
            ),
        )

    os.remove(input_file_path)


@celery_instance.task
def upload_file_to_storage(
    input_file_path: str,
    s3_key: str,
):
    with open(input_file_path, "rb") as f:
        data = f.read()

    try:
        asyncio.run(storage.upload_file(s3_key, data))
        log.info(f"Uploaded {s3_key}")
    except UploadFailureException as exc:
        log.error(f"Failed to upload {s3_key}")
        raise exc

    os.remove(input_file_path)
