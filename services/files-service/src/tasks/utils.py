from src.factories.file_adapter_factories import FileAdapterFactory
from src.video.transcoder import BITRATE_SETTINGS, HlsTranscoder


async def update_master_playlist_from_s3(s3_key: str, input_path: str):

    storage = FileAdapterFactory.s3_adapter_sync_factory()

    files = await storage.get_files_list(f"{s3_key}/")

    index_files = [f for f in files if f["Key"].endswith("index.m3u8")]

    lines = ["#EXTM3U", "#EXT-X-VERSION:3"]

    for obj in sorted(index_files, key=lambda o: o["Key"]):
        key = obj["Key"]
        quality = key.split("/")[-2]

        settings = BITRATE_SETTINGS.get(quality)

        target_height = int(quality.rstrip("p"))

        original_width, original_height = HlsTranscoder.get_video_resolution(input_path)
        width, height = HlsTranscoder.calculate_scaled_resolution(
            original_width, original_height, target_height
        )

        lines.append(
            f"#EXT-X-STREAM-INF:BANDWIDTH={bitrate_to_int(settings['bitrate'])},"
            f"AVERAGE-BANDWIDTH={bitrate_to_int(settings['bitrate'])},"
            f"RESOLUTION={width}x{height},"
            f'CODECS="avc1.4d401f,mp4a.40.2"'
        )
        lines.append(f"{quality}/index.m3u8")

    master_text = "\n".join(lines)
    await storage.upload_file(f"{s3_key}/master.m3u8", master_text.encode("utf-8"))


def bitrate_to_int(bitrate_str: str) -> int:
    return int(bitrate_str.rstrip("k")) * 1000
