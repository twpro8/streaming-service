from enum import Enum

from src.schemas.base import BaseSchema


class ContentType(str, Enum):
    films = "films"
    series = "series"


class FavoriteDTO(BaseSchema):
    id: int
    user_id: int
    content_id: int
    content_type: ContentType


class FavoriteAddRequestDTO(BaseSchema):
    content_id: int
    content_type: ContentType


class FavoriteAddDTO(BaseSchema):
    user_id: int
    content_id: int
    content_type: ContentType
