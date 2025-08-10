from uuid import UUID
from datetime import datetime, date

from src.enums import ZodiacSign
from src.schemas.base import BaseSchema, AtLeastOneFieldRequired


class ActorAddDTO(BaseSchema):
    first_name: str
    last_name: str
    birth_date: date
    zodiac_sign: ZodiacSign | None = None
    bio: str | None = None


class ActorDTO(ActorAddDTO):
    id: UUID
    created_at: datetime
    updated_at: datetime


class ActorPatchDTO(BaseSchema, AtLeastOneFieldRequired):
    first_name: str | None = None
    last_name: str | None = None
    birth_date: date | None = None
    zodiac_sign: ZodiacSign | None = None
    bio: str | None = None
