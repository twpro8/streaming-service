from src.schemas.base import BaseSchema


class SeasonAddRequestDTO(BaseSchema):
    title: str
    season_number: int


class SeasonAddDTO(SeasonAddRequestDTO):
    series_id: int


class SeasonPatchRequestDTO(BaseSchema):
    title: str | None = None
    season_number: int | None = None


class SeasonDTO(SeasonAddDTO):
    id: int
