import re
import shutil
from tempfile import NamedTemporaryFile

from fastapi import UploadFile


def save_to_temp_file(file: UploadFile):
    with NamedTemporaryFile(delete=False, suffix=file.filename) as tmp:
        shutil.copyfileobj(file.file, tmp)
        return tmp.name


def sanitize_filename(filename: str, max_length: int = 50) -> str:
    """
    Sanitize a filename by removing invalid characters and truncating its base name.
    """

    if "." not in filename:
        raise ValueError("Filename must contain an extension.")

    name, ext = filename.rsplit(".", 1)
    name = re.sub(r"[^a-zA-Z0-9_\-]", "_", name)

    return f"{name[:max_length]}.{ext}"
