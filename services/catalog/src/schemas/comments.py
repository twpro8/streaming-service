from datetime import datetime
from uuid import UUID

from src.schemas.base import BaseSchema
from src.schemas.pydantic_types import Str512
from src.enums import ContentType


class CommentAddRequestDTO(BaseSchema):
    content_id: UUID
    content_type: ContentType
    comment: Str512


class CommentAddDTO(BaseSchema):
    id: UUID
    user_id: UUID
    content_id: UUID
    content_type: ContentType
    comment: Str512


class CommentPutRequestDTO(BaseSchema):
    comment: Str512


class CommentDTO(CommentAddDTO):
    created_at: datetime
    updated_at: datetime
