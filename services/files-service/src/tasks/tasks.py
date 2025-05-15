import logging
import os
from typing import List
import asyncio
import subprocess
from tempfile import TemporaryDirectory
from pathlib import Path

from src import settings
from src.adapters.s3_adapter import S3Client
from src.core.enums import Qualities
from src.tasks.celery_app import celery_instance


log = logging.getLogger(__name__)


BITRATE_SETTINGS = {
    "360p": {"bitrate": "800k", "maxrate": "856k", "bufsize": "1200k"},
    "480p": {"bitrate": "1000k", "maxrate": "1070k", "bufsize": "1500k"},
    "720p": {"bitrate": "2800k", "maxrate": "2996k", "bufsize": "4200k"},
    "1080p": {"bitrate": "5000k", "maxrate": "5350k", "bufsize": "7500k"},
}


def transcode_to_hls(input_path: str, output_dir: Path, qualities: List[Qualities]):
    for quality in qualities:
        height = quality.rstrip("p")
        output_quality_dir = output_dir / quality
        output_quality_dir.mkdir(parents=True, exist_ok=True)

        output_playlist = f"{output_quality_dir}/index.m3u8"
        output_segment = f"{output_quality_dir}/segment_%03d.ts"

        settings = BITRATE_SETTINGS.get(
            quality,
            {
                "bitrate": "1400k",
                "maxrate": "1498k",
                "bufsize": "2100k",
            },
        )

        cmd = [
            "ffmpeg",
            "-i", input_path,
            "-vf", f"scale=-2:{height}",
            "-ar", "48000",
            "-c:v", "libx264",
            "-profile:v", "main",
            "-crf", "20",
            "-g", "48",
            "-keyint_min", "48",
            "-sc_threshold", "0",
            "-b:v", settings["bitrate"],
            "-maxrate", settings["maxrate"],
            "-bufsize", settings["bufsize"],
            "-c:a", "aac",
            "-b:a", "128k",
            "-hls_time", "4",
            "-hls_playlist_type", "vod",
            "-hls_segment_filename", output_segment,
            output_playlist
        ]

        subprocess.run(cmd)


@celery_instance.task
def process_video_and_upload_to_s3(
    input_file_path: str,
    s3_key: int,
    qualities: List[Qualities],
):
    s3_client = S3Client(
        access_key=settings.S3_ACCESS_KEY,
        secret_key=settings.S3_SECRET_KEY,
        endpoint_url=settings.S3_ENDPOINT_URL,
        bucket_name=settings.S3_BUCKET_NAME,
    )

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
    s3_client = S3Client(
        access_key=settings.S3_ACCESS_KEY,
        secret_key=settings.S3_SECRET_KEY,
        endpoint_url=settings.S3_ENDPOINT_URL,
        bucket_name=settings.S3_BUCKET_NAME,
    )

    with open(input_file_path, "rb") as f:
        data = f.read()

    success = asyncio.run(s3_client.upload_file(s3_key, data))
    if success:
        log.info(f"Uploaded {s3_key}")
    else:
        log.error(f"Failed to upload {s3_key}")

    os.remove(input_file_path)
