from datetime import datetime, date
from typing import List
from uuid import UUID, uuid4

from sqlalchemy import String, Date, Enum, DateTime, text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.enums import ZodiacSign
from src.models.base import Base


class DirectorORM(Base):
    __tablename__ = "directors"
    __table_args__ = (
        UniqueConstraint(
            "first_name",
            "last_name",
            "birth_date",
            name="uq_director",
        ),
    )

    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )
    first_name: Mapped[str] = mapped_column(String(48))
    last_name: Mapped[str] = mapped_column(String(48))
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    zodiac_sign: Mapped[ZodiacSign | None] = mapped_column(Enum(ZodiacSign), nullable=True)
    bio: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('UTC', now())"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('UTC', now())"),
    )  # Make sure you have added the trigger to the migration.

    # Relationships
    movies: Mapped[List["MovieORM"]] = relationship(
        secondary="movie_director_associations",
        back_populates="directors",
    )
    shows: Mapped[List["ShowORM"]] = relationship(
        secondary="show_director_associations",
        back_populates="directors",
    )

    def __repr__(self):
        return (
            f"<DirectorORM("
            f"id={self.id!r}, "
            f"first_name={self.first_name!r}, "
            f"last_name={self.last_name!r}, "
            f"birth_date={self.birth_date!r}, "
            f"zodiac_sign={self.zodiac_sign!r}, "
            f"bio={self.bio!r}, "
            f"created_at={self.created_at!r}, "
            f"updated_at={self.updated_at!r})>"
        )
