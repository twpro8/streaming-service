from uuid import UUID
from datetime import datetime

from pydantic import Field

from src.schemas.base import BaseSchema
from src.schemas.pydatic_types import Str256, EmailStr


class RefreshTokenAddDTO(BaseSchema):
    id: UUID
    user_id: UUID
    ip: str = Field(min_length=7, max_length=15)
    user_agent: Str256
    expires_at: datetime


class RefreshTokenDTO(RefreshTokenAddDTO):
    created_at: datetime


class RefreshTokenUpdateDTO(BaseSchema):
    id: UUID
    expires_at: datetime


class ClientInfo(BaseSchema):
    ip: str = Field(min_length=7, max_length=15)
    user_agent: str


class VerifyEmailRequestDTO(BaseSchema):
    email: EmailStr
    code: str
