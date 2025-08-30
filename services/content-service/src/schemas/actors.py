from uuid import UUID
from datetime import datetime

from src.enums import ZodiacSign
from src.schemas.base import BaseSchema, AtLeastOneFieldMixin
from src.schemas.pydantic_types import Date, Str48, Str1024


class ActorAddRequestDTO(BaseSchema):
    first_name: Str48
    last_name: Str48
    birth_date: Date
    zodiac_sign: ZodiacSign | None = None
    bio: Str1024 | None = None


class ActorAddDTO(ActorAddRequestDTO):
    id: UUID


class ActorDTO(ActorAddDTO):
    created_at: datetime
    updated_at: datetime


class ActorPatchDTO(BaseSchema, AtLeastOneFieldMixin):
    first_name: Str48 | None = None
    last_name: Str48 | None = None
    birth_date: Date | None = None
    zodiac_sign: ZodiacSign | None = None
    bio: Str1024 | None = None


class MovieActorDTO(BaseSchema):
    movie_id: UUID
    actor_id: UUID


class ShowActorDTO(BaseSchema):
    show_id: UUID
    actor_id: UUID
