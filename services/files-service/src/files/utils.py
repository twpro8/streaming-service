import re
import shutil
from tempfile import NamedTemporaryFile

from fastapi import UploadFile


def save_to_temp_file(file: UploadFile):
    with NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
        shutil.copyfileobj(file.file, tmp)
        return tmp.name


def generate_film_s3_key(film_id: int) -> str:
    return f"films/{film_id}"


def generate_episode_s3_key(series_id: int, episode_number: int) -> str:
    return f"series/{series_id}/episodes/{episode_number}"


def generate_image_s3_key(content_type: str, content_id: int, filename: str) -> str:
    return f"{content_type}/{content_id}/covers/{filename}"


def sanitize_filename(filename: str, max_length: int = 50) -> str:
    """
    Sanitize a filename by removing invalid characters and truncating its base name.
    """

    if "." not in filename:
        raise ValueError("Filename must contain an extension.")

    name, ext = filename.rsplit(".", 1)
    name = re.sub(r"[^a-zA-Z0-9_\-]", "_", name)

    return f"{name[:max_length]}.{ext}"
