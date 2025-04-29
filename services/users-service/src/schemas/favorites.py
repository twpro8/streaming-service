from datetime import datetime

from enum import Enum

from src.schemas.base import BaseSchema


class ContentType(str, Enum):
    films = "film"
    series = "series"


class FavoriteAddRequestDTO(BaseSchema):
    content_id: int
    content_type: ContentType


class FavoriteAddDTO(FavoriteAddRequestDTO):
    user_id: int


class FavoriteDTO(FavoriteAddDTO):
    id: int
    created_at: datetime
