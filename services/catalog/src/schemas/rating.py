from uuid import UUID


from pydantic import condecimal

from src.schemas.base import BaseSchema
from src.enums import ContentType


class RatingUpdateDTO(BaseSchema):
    value: condecimal(max_digits=3, decimal_places=1, ge=1, le=10)


class RatingAddRequestDTO(RatingUpdateDTO):
    content_id: UUID
    content_type: ContentType


class RatingAddDTO(RatingUpdateDTO):
    user_id: UUID
    content_id: UUID


class RatingDTO(RatingAddDTO):
    id: UUID


class RatingAggregateDTO(BaseSchema):
    content_id: UUID
    rating_sum: condecimal(max_digits=10, decimal_places=1)
    rating_count: int
    rating_avg: condecimal(max_digits=3, decimal_places=1, ge=1, le=10)


class RatingAggregateAddUpdateDTO(BaseSchema):
    content_id: UUID
    delta_sum: condecimal(max_digits=10, decimal_places=1)
    delta_count: int
