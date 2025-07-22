import re
from uuid import UUID

from src.config import settings
from src.exceptions import (
    InvalidContentTypeException,
    NoExtensionException,
    ExtensionTooLongException,
)


def sanitize_filename(
    filename: str,
    max_length: int = 50,
    max_ext_length: int = 3,
) -> str:
    """
    Sanitize a filename by removing invalid characters and truncating its base name.
    """

    try:
        name, ext = filename.rsplit(".", 1)
    except ValueError:
        raise NoExtensionException

    if len(ext) > max_ext_length:
        raise ExtensionTooLongException(
            detail=f"Extension too long. Max length must be less than: {max_ext_length}",
        )

    name = re.sub(r"[^a-zA-Z0-9_\-]", "_", name)

    return f"{name[:max_length]}.{ext}"


def validate_video_mime_type(mime_type: str) -> None:
    if mime_type not in settings.INPUT_VIDEO_MIMO:
        raise InvalidContentTypeException


def get_base_video_storage_key(content_id: UUID):
    return f"videos/{content_id}"


def get_original_file_storage_key(storage_base_key: str, filename: str) -> str:
    return f"{storage_base_key}/original/{filename}"
