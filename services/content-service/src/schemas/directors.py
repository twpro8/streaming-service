from datetime import datetime
from uuid import UUID

from src.enums import ZodiacSign
from src.schemas.base import BaseSchema, AtLeastOneFieldMixin
from src.schemas.pydantic_types import Str48, Date, Str1024


class DirectorAddRequestDTO(BaseSchema):
    first_name: Str48
    last_name: Str48
    birth_date: Date | None = None
    zodiac_sign: ZodiacSign | None = None
    bio: Str1024 | None = None


class DirectorAddDTO(DirectorAddRequestDTO):
    id: UUID


class DirectorDTO(DirectorAddDTO):
    id: UUID
    created_at: datetime
    updated_at: datetime


class DirectorPatchDTO(BaseSchema, AtLeastOneFieldMixin):
    first_name: Str48 | None = None
    last_name: Str48 | None = None
    birth_date: Date | None = None
    zodiac_sign: ZodiacSign | None = None
    bio: Str1024 | None = None


class MovieDirectorDTO(BaseSchema):
    movie_id: UUID
    director_id: UUID


class ShowDirectorDTO(BaseSchema):
    show_id: UUID
    director_id: UUID
