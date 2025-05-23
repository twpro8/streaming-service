from uuid import UUID

from pydantic import Field

from src.schemas.base import BaseSchema
from src.schemas.pydantic_types import ContentType, IDInt


class CommentAddRequestDTO(BaseSchema):
    content_id: UUID
    content_type: ContentType  # Example: "film" or "series"
    text: str = Field(min_length=1, max_length=1024)


class CommentAddDTO(BaseSchema):
    film_id: UUID | None = None
    series_id: UUID | None = None
    user_id: IDInt
    text: str = Field(min_length=1, max_length=1024)


class CommentDTO(CommentAddDTO):
    id: UUID
