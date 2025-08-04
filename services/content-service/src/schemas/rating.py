from uuid import UUID

from datetime import datetime

from src.schemas.base import BaseSchema
from src.schemas.pydantic_types import IDInt, ContentType, RatingDecimal


class RatingAddRequestDTO(BaseSchema):
    content_id: UUID
    content_type: ContentType
    value: RatingDecimal


class RatingAddDTO(BaseSchema):
    user_id: IDInt
    content_id: UUID
    value: RatingDecimal


class RatingDTO(RatingAddDTO):
    id: UUID
    created_at: datetime
