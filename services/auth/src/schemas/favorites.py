from datetime import datetime

from enum import Enum

from src.schemas.base import BaseSchema
from src.schemas.pydatic_types import IDInt


class ContentType(str, Enum):
    films = "film"
    series = "series"


class FavoriteAddRequestDTO(BaseSchema):
    content_id: IDInt
    content_type: ContentType


class FavoriteAddDTO(FavoriteAddRequestDTO):
    user_id: IDInt


class FavoriteDTO(FavoriteAddDTO):
    id: IDInt
    created_at: datetime
