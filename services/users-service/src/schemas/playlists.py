from typing import List

from datetime import datetime

from src.schemas.base import BaseSchema
from src.schemas.favorites import ContentType
from src.schemas.pydatic_types import IDInt


class PlaylistAddRequestDTO(BaseSchema):
    name: str


class PlaylistAddDTO(PlaylistAddRequestDTO):
    user_id: IDInt


class PlaylistDTO(PlaylistAddDTO):
    id: IDInt
    created_at: datetime


class PlaylistItemAddRequestDTO(BaseSchema):
    content_id: IDInt
    content_type: ContentType


class PlaylistItemAddDTO(PlaylistItemAddRequestDTO):
    playlist_id: IDInt


class PlaylistItemDTO(PlaylistItemAddRequestDTO):
    id: IDInt
    added_at: datetime


class PlaylistWithRelsDTO(PlaylistDTO):
    items: List[PlaylistItemDTO]
