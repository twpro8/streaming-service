from typing import Annotated

from pydantic import EmailStr, Field

email_str = Annotated[EmailStr, Field(min_length=5, max_length=255)]
password_str = Annotated[str, Field(min_length=6, max_length=255)]
