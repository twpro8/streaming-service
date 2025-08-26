from datetime import datetime
from uuid import UUID

from src.enums import ZodiacSign
from src.schemas.base import BaseSchema, AtLeastOneFieldMixin
from src.schemas.pydantic_types import IDInt, Str48, BirthDate, Str256


class DirectorAddDTO(BaseSchema):
    first_name: Str48
    last_name: Str48
    birth_date: BirthDate | None = None
    zodiac_sign: ZodiacSign | None = None
    bio: Str256 | None = None


class DirectorDTO(DirectorAddDTO):
    id: IDInt
    created_at: datetime
    updated_at: datetime


class DirectorPatchDTO(BaseSchema, AtLeastOneFieldMixin):
    first_name: Str48 | None = None
    last_name: Str48 | None = None
    birth_date: BirthDate | None = None
    zodiac_sign: ZodiacSign | None = None
    bio: Str256 | None = None


class MovieDirectorDTO(BaseSchema):
    movie_id: UUID
    director_id: IDInt


class ShowDirectorDTO(BaseSchema):
    show_id: UUID
    director_id: IDInt
