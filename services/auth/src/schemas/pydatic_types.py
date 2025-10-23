from datetime import date, timedelta
from typing import Annotated

from pydantic import Field, EmailStr, BeforeValidator


EmailStr = Annotated[EmailStr, Field(min_length=5, max_length=128)]
PasswordStr = Annotated[str, Field(min_length=6, max_length=128)]

Date = Annotated[date, Field(le=date.today() - timedelta(weeks=365), ge=date(1900, 1, 1))]
Str48 = Annotated[str, Field(min_length=2, max_length=48)]
Str100 = Annotated[str, Field(min_length=2, max_length=100)]
Str128 = Annotated[str, Field(min_length=2, max_length=128)]
Str256 = Annotated[str, Field(min_length=2, max_length=256)]
Str512 = Annotated[str, Field(min_length=2, max_length=512)]
Str1024 = Annotated[str, Field(min_length=2, max_length=1024)]

PositiveInt = Annotated[int, Field(gt=0)]

StrAnyUrl = Annotated[str, BeforeValidator(lambda v: str(v) if v else v)]
