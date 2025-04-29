from datetime import datetime

from src.schemas.base import BaseSchema


class PlaylistAddRequestDTO(BaseSchema):
    name: str


class PlaylistAddDTO(PlaylistAddRequestDTO):
    user_id: int


class PlaylistDTO(PlaylistAddDTO):
    id: int
    created_at: datetime
