from datetime import datetime
from uuid import UUID

from src.core.base.schema import BaseSchema
from src.core.enums import ContentType


class FileAddDTO(BaseSchema):
    content_id: UUID
    filename: str
    s3_key: str
    mime_type: str
    size: int
    content_type: ContentType


class FileDTO(FileAddDTO):
    id: UUID
    created_at: datetime
