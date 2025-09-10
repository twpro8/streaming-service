from datetime import datetime
from typing import Annotated
from uuid import UUID

from uuid_extensions import uuid7
from sqlalchemy import String, DateTime, text
from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PG_UUID


int_pk = Annotated[int, mapped_column(primary_key=True)]
uuid_pk = Annotated[
    UUID,
    mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid7,
    ),
]

str_2 = Annotated[str, 2]
str_32 = Annotated[str, 32]
str_48 = Annotated[str, 48]
str_64 = Annotated[str, 64]
str_256 = Annotated[str, 256]
str_512 = Annotated[str, 512]
str_1024 = Annotated[str, 1024]

created_at = Annotated[
    datetime,
    mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('UTC', now())"),
    ),
]


class Base(DeclarativeBase):
    type_annotation_map = {
        UUID: PG_UUID(as_uuid=True),
        str_2: String(2),
        str_32: String(32),
        str_48: String(48),
        str_64: String(64),
        str_256: String(256),
        str_512: String(512),
        str_1024: String(1024),
    }
