import logging
import subprocess
from typing import List
from pathlib import Path

from src.core.enums import Qualities


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
