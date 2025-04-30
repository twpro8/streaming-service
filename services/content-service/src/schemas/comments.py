from pydantic import Field

from src.schemas.base import BaseSchema
from src.schemas.pydantic_types import ContentType, TypeID


class CommentAddRequestDTO(BaseSchema):
    content_id: TypeID
    content_type: ContentType # Example: "film" or "series"
    text: str = Field(min_length=1, max_length=1024)


class CommentAddDTO(BaseSchema):
    film_id: TypeID | None = None
    series_id: TypeID | None = None
    user_id: TypeID
    text: str = Field(min_length=1, max_length=1024)


class CommentDTO(CommentAddDTO):
    id: TypeID
