from uuid import UUID

from datetime import datetime

from pydantic import condecimal

from src.schemas.base import BaseSchema
from src.schemas.pydantic_types import IDInt
from src.enums import ContentType


class RatingAddRequestDTO(BaseSchema):
    content_id: UUID
    content_type: ContentType
    value: condecimal(max_digits=3, decimal_places=1, ge=1, le=10)


class RatingAddDTO(BaseSchema):
    user_id: IDInt
    content_id: UUID
    value: condecimal(max_digits=3, decimal_places=1, ge=1, le=10)


class RatingDTO(RatingAddDTO):
    id: UUID
    created_at: datetime
