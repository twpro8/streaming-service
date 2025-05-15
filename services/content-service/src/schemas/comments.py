from pydantic import Field

from src.schemas.base import BaseSchema
from src.schemas.pydantic_types import ContentType, IDInt


class CommentAddRequestDTO(BaseSchema):
    content_id: IDInt
    content_type: ContentType  # Example: "film" or "series"
    text: str = Field(min_length=1, max_length=1024)


class CommentAddDTO(BaseSchema):
    film_id: IDInt | None = None
    series_id: IDInt | None = None
    user_id: IDInt
    text: str = Field(min_length=1, max_length=1024)


class CommentDTO(CommentAddDTO):
    id: IDInt
