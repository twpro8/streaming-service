from datetime import datetime
from uuid import UUID

from pydantic import Field

from src.enums import ContentType
from src.schemas.base import BaseSchema


class FileAddDTO(BaseSchema):
    content_id: UUID
    filename: str = Field(max_length=255)
    storage_path: str = Field(max_length=255)
    mime_type: str = Field(max_length=255)
    size_in_bytes: int
    content_type: ContentType


class FileDTO(FileAddDTO):
    created_at: datetime
