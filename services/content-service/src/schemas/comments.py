from datetime import datetime
from uuid import UUID

from src.schemas.base import BaseSchema
from src.schemas.pydantic_types import IDInt, TextStr255
from src.enums import ContentType


class CommentAddRequestDTO(BaseSchema):
    content_id: UUID
    content_type: ContentType
    comment: TextStr255


class CommentAddDTO(BaseSchema):
    id: UUID
    movie_id: UUID | None = None
    show_id: UUID | None = None
    user_id: IDInt
    comment: TextStr255


class CommentPutRequestDTO(BaseSchema):
    comment: TextStr255


class CommentDTO(CommentAddDTO):
    created_at: datetime
    updated_at: datetime
