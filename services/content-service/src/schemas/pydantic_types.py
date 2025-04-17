from typing import Annotated

from pydantic import Field


TypeTitle = Annotated[
    str, Field(min_length=5, max_length=255, title="Pydantic Type: Title, String 255")
]
TypeDuration = Annotated[int, Field(ge=1, le=9999, title="Pydantic Type: Duration, Integer 9999")]
TypeID = Annotated[int, Field(ge=1, le=2147483647, title="Pydantic Type: ID, Integer 32 bit")]
TypeRating = Annotated[float, Field(ge=0.0, le=10.0, title="Pydantic Type: Rating, Float 10.0")]
