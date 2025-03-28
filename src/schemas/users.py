from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserDTO(BaseModel):
    id: int
    email: EmailStr
    name: str
    bio: str | None
    avatar: str | None
    provider: str | None
    created_at: datetime
    is_admin: bool
    is_active: bool
