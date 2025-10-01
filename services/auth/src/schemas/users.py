from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel


class UserAddDTO(BaseModel):
    id: UUID
    name: str
    first_name: str
    last_name: str | None = None
    email: str
    birth_date: date | None = None
    bio: str | None = None
    picture: str | None = None
    provider_name: str | None = None
    password_hash: str | None = None
    refresh_token_hash: str | None = None


class UserDTO(BaseModel):
    id: UUID
    name: str
    first_name: str
    last_name: str | None
    email: str
    birth_date: date | None
    bio: str | None
    picture: str | None
    provider_name: str | None
    is_admin: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime


class DBUserDTO(UserDTO):
    password_hash: str | None
    refresh_token_hash: str | None
