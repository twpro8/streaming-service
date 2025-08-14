from uuid import UUID
from datetime import datetime

from src.enums import ZodiacSign
from src.schemas.base import BaseSchema, AtLeastOneFieldRequired
from src.schemas.pydantic_types import BirthDate, Str48, Str128


class ActorAddRequestDTO(BaseSchema):
    first_name: Str48
    last_name: Str48
    birth_date: BirthDate
    zodiac_sign: ZodiacSign | None = None
    bio: Str128 | None = None


class ActorAddDTO(BaseSchema):
    id: UUID
    first_name: Str48
    last_name: Str48
    birth_date: BirthDate
    zodiac_sign: ZodiacSign | None = None
    bio: Str128 | None = None


class ActorDTO(ActorAddDTO):
    created_at: datetime
    updated_at: datetime


class ActorPatchDTO(BaseSchema, AtLeastOneFieldRequired):
    first_name: Str48 | None = None
    last_name: Str48 | None = None
    birth_date: BirthDate | None = None
    zodiac_sign: ZodiacSign | None = None
    bio: Str128 | None = None


class FilmActorDTO(BaseSchema):
    film_id: UUID
    actor_id: UUID


class SeriesActorDTO(BaseSchema):
    series_id: UUID
    actor_id: UUID
