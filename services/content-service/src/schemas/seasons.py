from datetime import datetime
from uuid import UUID

from pydantic import Field

from src.schemas.base import BaseSchema, AtLeastOneFieldRequired
from src.schemas.pydantic_types import TitleStr


class SeasonAddRequestDTO(BaseSchema):
    show_id: UUID
    title: TitleStr
    season_number: int = Field(default=1, ge=1, le=500, title="Season Number")


class SeasonAddDTO(SeasonAddRequestDTO):
    id: UUID


class SeasonPatchRequestDTO(BaseSchema, AtLeastOneFieldRequired):
    title: TitleStr | None = None
    season_number: int | None = Field(default=None, ge=1, le=500, title="Season Number")


class SeasonDTO(SeasonAddDTO):
    created_at: datetime
    updated_at: datetime
