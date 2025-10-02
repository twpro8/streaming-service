from uuid import UUID
from datetime import datetime

from src.schemas.base import BaseSchema
from src.schemas.pydatic_types import Str256


class RefreshTokenAddDTO(BaseSchema):
    id: UUID
    user_id: UUID
    token_hash: Str256


class RefreshTokenDTO(RefreshTokenAddDTO):
    created_at: datetime
    updated_at: datetime
