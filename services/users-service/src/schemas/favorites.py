from enum import Enum

from pydantic import BaseModel


class ContentType(str, Enum):
    film = "film"
    series = "series"


class FavoriteDTO(BaseModel):
    id: int
    user_id: int
    content_id: int
    content_type: ContentType


class FavoriteAddRequestDTO(BaseModel):
    content_id: int
    content_type: ContentType


class FavoriteAddDTO(BaseModel):
    user_id: int
    content_id: int
    content_type: ContentType
