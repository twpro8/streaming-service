from typing import List

from datetime import datetime

from src.schemas.base import BaseSchema
from src.schemas.favorites import ContentType
from src.schemas.pydatic_types import TypeID


class PlaylistAddRequestDTO(BaseSchema):
    name: str


class PlaylistAddDTO(PlaylistAddRequestDTO):
    user_id: TypeID


class PlaylistDTO(PlaylistAddDTO):
    id: TypeID
    created_at: datetime


class PlaylistItemAddRequestDTO(BaseSchema):
    content_id: TypeID
    content_type: ContentType


class PlaylistItemAddDTO(PlaylistItemAddRequestDTO):
    playlist_id: TypeID


class PlaylistItemDTO(PlaylistItemAddRequestDTO):
    id: TypeID
    added_at: datetime


class PlaylistWithRelsDTO(PlaylistDTO):
    items: List[PlaylistItemDTO]
