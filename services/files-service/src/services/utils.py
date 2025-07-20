import re

from src.config import settings
from src.exceptions import InvalidContentTypeException, NoExtensionException


def sanitize_filename(filename: str, max_length: int = 50) -> str:
    """
    Sanitize a filename by removing invalid characters and truncating its base name.
    """

    if "." not in filename:
        raise NoExtensionException

    name, ext = filename.rsplit(".", 1)
    name = re.sub(r"[^a-zA-Z0-9_\-]", "_", name)

    return f"{name[:max_length]}.{ext}"


def validate_mime_type(mime_type: str) -> None:
    if mime_type not in settings.INPUT_VIDEO_MIMO:
        raise InvalidContentTypeException
