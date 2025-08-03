from datetime import date
from decimal import Decimal

from enum import Enum
from typing import Annotated

from pydantic import Field, condecimal


# Reusable Annotated Types

TitleStr = Annotated[
    str,
    Field(
        min_length=3,
        max_length=255,
        title="Title",
        description="Title string from 3 to 255 characters",
        examples=["John's Journey"],
    ),
]

DurationInt = Annotated[
    int,
    Field(
        ge=1,
        le=512,
        title="Duration",
        description="Duration in minutes (1 to 9999)",
        examples=[110],
    ),
]

IDInt = Annotated[
    int,
    Field(
        ge=1,
        le=2_147_483_647,
        title="ID",
        description="Positive 32-bit integer identifier",
        examples=[123],
    ),
]

RatingDecimal = Annotated[
    Decimal,
    condecimal(gt=0, le=10, max_digits=3, decimal_places=1),
    Field(
        title="Rating",
        description="User rating from 0.1 to 10.0 with one decimal place",
        examples=[8.5],
    ),
]

DescriptionStr = Annotated[
    str,
    Field(
        min_length=3,
        max_length=255,
        title="Description",
        description="Detailed description of the content",
        examples=["A thrilling journey of John through mysterious lands."],
    ),
]

DirectorStr = Annotated[str, Field(min_length=3, max_length=48)]

ReleaseYearDate = Annotated[date, Field(le=date.today(), ge=date(1000, 1, 1))]

TextStr255 = Annotated[
    str,
    Field(
        min_length=3,
        max_length=255,
    ),
]


# Enum for content type


class ContentType(str, Enum):
    film = "film"
    series = "series"

    def __str__(self):
        return self.value
