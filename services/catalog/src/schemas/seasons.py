from datetime import datetime
from uuid import UUID

from src.schemas.base import BaseSchema, AtLeastOneFieldMixin
from src.schemas.pydantic_types import Str256, PositiveInt


class SeasonAddRequestDTO(BaseSchema):
    show_id: UUID
    title: Str256
    season_number: PositiveInt


class SeasonAddDTO(SeasonAddRequestDTO):
    id: UUID


class SeasonPatchRequestDTO(BaseSchema, AtLeastOneFieldMixin):
    title: Str256 | None = None
    season_number: PositiveInt | None = None


class SeasonDTO(SeasonAddDTO):
    created_at: datetime
    updated_at: datetime
