from enum import Enum
from typing import Annotated

from pydantic import Field, EmailStr


email_str = Annotated[EmailStr, Field(min_length=5, max_length=255)]
password_str = Annotated[str, Field(min_length=6, max_length=255)]


# Reusable Annotated Types


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


# Enum for content type


class ContentType(str, Enum):
    film = "film"
    series = "series"
