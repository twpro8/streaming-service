from uuid import UUID

from datetime import datetime

from src.schemas.base import BaseSchema
from src.schemas.pydantic_types import IDInt, ContentType, RatingDecimal


class RatingAddRequestDTO(BaseSchema):
    content_id: UUID
    content_type: ContentType
    rating: RatingDecimal


class RatingAddDTO(RatingAddRequestDTO):
    user_id: IDInt


class RatingDTO(RatingAddDTO):
    id: UUID
    created_at: datetime
