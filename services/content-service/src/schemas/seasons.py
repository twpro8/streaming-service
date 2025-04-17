from src.schemas.base import BaseSchema
from src.schemas.pydantic_types import TypeID, TypeTitle


class SeasonAddRequestDTO(BaseSchema):
    title: TypeTitle
    season_number: int


class SeasonAddDTO(SeasonAddRequestDTO):
    series_id: TypeID


class SeasonPatchRequestDTO(BaseSchema):
    title: TypeTitle | None = None
    season_number: int | None = None


class SeasonDTO(SeasonAddDTO):
    id: TypeID
