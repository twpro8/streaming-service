from datetime import date
from typing import Annotated
from decimal import Decimal

from pydantic import Field, condecimal, BeforeValidator

RatingDecimal = Annotated[
    Decimal,
    condecimal(gt=0, le=10, max_digits=3, decimal_places=1),
    Field(title="Rating", examples=[8.5]),
]

Date = Annotated[date, Field(le=date.today(), ge=date(1000, 1, 1))]
Str48 = Annotated[str, Field(min_length=2, max_length=48)]
Str100 = Annotated[str, Field(min_length=2, max_length=100)]
Str128 = Annotated[str, Field(min_length=2, max_length=128)]
Str256 = Annotated[str, Field(min_length=2, max_length=256)]
Str512 = Annotated[str, Field(min_length=2, max_length=512)]
Str1024 = Annotated[str, Field(min_length=2, max_length=1024)]

PositiveInt = Annotated[int, Field(gt=0)]

StrAnyUrl = Annotated[str, BeforeValidator(lambda v: str(v) if v else v)]
