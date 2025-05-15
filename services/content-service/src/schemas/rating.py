from datetime import datetime

from src.schemas.base import BaseSchema
from src.schemas.pydantic_types import IDInt, ContentType, RatingDecimal


class RatingAddRequestDTO(BaseSchema):
    content_id: IDInt
    content_type: ContentType
    rating: RatingDecimal


class RatingAddDTO(RatingAddRequestDTO):
    user_id: IDInt


class RatingDTO(RatingAddDTO):
    id: IDInt
    created_at: datetime
