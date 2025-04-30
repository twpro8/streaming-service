from typing import List

from datetime import datetime

from src.schemas.base import BaseSchema
from src.schemas.favorites import ContentType


class PlaylistAddRequestDTO(BaseSchema):
    name: str


class PlaylistAddDTO(PlaylistAddRequestDTO):
    user_id: int


class PlaylistDTO(PlaylistAddDTO):
    id: int
    created_at: datetime


class PlaylistItemAddRequestDTO(BaseSchema):
    content_id: int
    content_type: ContentType


class PlaylistItemAddDTO(PlaylistItemAddRequestDTO):
    playlist_id: int


class PlaylistItemDTO(PlaylistItemAddRequestDTO):
    id: int
    added_at: datetime


class PlaylistWithRelsDTO(PlaylistDTO):
    items: List[PlaylistItemDTO]
