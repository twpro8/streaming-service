from datetime import datetime
from uuid import UUID

from src.schemas.base import BaseSchema
from src.schemas.pydantic_types import ContentType, IDInt, TextStr255


class CommentAddRequestDTO(BaseSchema):
    content_id: UUID
    content_type: ContentType
    comment: TextStr255


class CommentAddDTO(BaseSchema):
    film_id: UUID | None = None
    series_id: UUID | None = None
    user_id: IDInt
    comment: TextStr255


class CommentPutRequestDTO(BaseSchema):
    comment: TextStr255


class CommentDTO(CommentAddDTO):
    id: UUID
    created_at: datetime
