import logging
import subprocess
from typing import List, Tuple
from pathlib import Path
from src.enums import Qualities


log = logging.getLogger(__name__)


BITRATE_SETTINGS = {
    "360p": {"bitrate": "800k", "maxrate": "856k", "bufsize": "1200k"},
    "480p": {"bitrate": "1000k", "maxrate": "1070k", "bufsize": "1500k"},
    "720p": {"bitrate": "2800k", "maxrate": "2996k", "bufsize": "4200k"},
    "1080p": {"bitrate": "5000k", "maxrate": "5350k", "bufsize": "7500k"},
}


class HlsTranscoder:
    def __init__(self, input_path: str, output_dir: Path, qualities: List[Qualities]):
        self.input_path = input_path
        self.output_dir = output_dir
        self.qualities = qualities

    def transcode(self):
        original_width, original_height = self.get_video_resolution(self.input_path)

        for quality in self.qualities:
            target_height = int(quality.rstrip("p"))

            width, height = self.calculate_scaled_resolution(
                original_width, original_height, target_height
            )

            output_quality_dir = self.output_dir / quality
            output_quality_dir.mkdir(parents=True, exist_ok=True)

            output_playlist = f"{output_quality_dir}/index.m3u8"
            output_segment = f"{output_quality_dir}/segment_%03d.ts"

            settings = BITRATE_SETTINGS[quality]

            cmd = [
                "ffmpeg",
                "-i",
                self.input_path,
                "-vf",
                f"scale={width}:{height}",
                "-ar",
                "48000",
                "-c:v",
                "libx264",
                "-profile:v",
                "main",
                "-crf",
                "20",
                "-g",
                "48",
                "-keyint_min",
                "48",
                "-sc_threshold",
                "0",
                "-b:v",
                settings["bitrate"],
                "-maxrate",
                settings["maxrate"],
                "-bufsize",
                settings["bufsize"],
                "-c:a",
                "aac",
                "-b:a",
                "128k",
                "-hls_time",
                "4",
                "-hls_playlist_type",
                "vod",
                "-hls_segment_filename",
                output_segment,
                output_playlist,
            ]

            subprocess.run(cmd, check=True)

    @staticmethod
    def get_video_resolution(input_path: str) -> Tuple[int, int]:
        cmd = [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height",
            "-of",
            "csv=s=x:p=0",
            input_path,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        width, height = map(int, result.stdout.strip().split("x"))
        return width, height

    @staticmethod
    def calculate_scaled_resolution(
        original_width: int, original_height: int, target_height: int
    ) -> Tuple[int, int]:
        scaled_width = (original_width * target_height) // original_height
        scaled_width = scaled_width - (scaled_width % 2)
        return scaled_width, target_height
