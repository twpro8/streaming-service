from uuid import UUID
from datetime import datetime

from pydantic import Field, EmailStr

from src.schemas.base import BaseSchema
from src.schemas.pydatic_types import Str256, PasswordStr


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


class EmailVerifyRequestDTO(BaseSchema):
    email: EmailStr
    code: str = Field(min_length=6, max_length=6)


class PasswordResetRequestDTO(EmailVerifyRequestDTO):
    new_password: PasswordStr


class PasswordChangeRequestDTO(BaseSchema):
    password: str
    new_password: PasswordStr
