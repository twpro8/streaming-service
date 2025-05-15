from src.schemas.base import BaseSchema
from src.schemas.pydantic_types import IDInt, TitleStr


class SeasonAddRequestDTO(BaseSchema):
    title: TitleStr
    season_number: int


class SeasonAddDTO(SeasonAddRequestDTO):
    series_id: IDInt


class SeasonPatchRequestDTO(BaseSchema):
    title: TitleStr | None = None
    season_number: int | None = None


class SeasonDTO(SeasonAddDTO):
    id: IDInt
