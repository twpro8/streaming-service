from datetime import datetime

from enum import Enum

from src.schemas.base import BaseSchema
from src.schemas.pydatic_types import TypeID


class ContentType(str, Enum):
    films = "film"
    series = "series"


class FavoriteAddRequestDTO(BaseSchema):
    content_id: TypeID
    content_type: ContentType


class FavoriteAddDTO(FavoriteAddRequestDTO):
    user_id: TypeID


class FavoriteDTO(FavoriteAddDTO):
    id: TypeID
    created_at: datetime
