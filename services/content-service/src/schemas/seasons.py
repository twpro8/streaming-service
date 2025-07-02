from uuid import UUID

from pydantic import Field

from src.schemas.base import BaseSchema
from src.schemas.pydantic_types import TitleStr


class SeasonAddRequestDTO(BaseSchema):
    title: TitleStr
    season_number: int = Field(default=1, ge=1, le=500, title="Season Number")


class SeasonAddDTO(SeasonAddRequestDTO):
    series_id: UUID


class SeasonPatchRequestDTO(BaseSchema):
    title: TitleStr | None = None
    season_number: int | None = None


class SeasonDTO(SeasonAddDTO):
    id: UUID
