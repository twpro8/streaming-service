from datetime import datetime, date
from typing import List

from sqlalchemy import String, Date, Enum, DateTime, text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.enums import ZodiacSign
from src.models.base import Base


class DirectorORM(Base):
    __tablename__ = "directors"
    __table_args__ = (
        UniqueConstraint(
            "first_name",
            "last_name",
            "birth_date",
            name="unique_directors_full_identity",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    first_name: Mapped[str] = mapped_column(String(48))
    last_name: Mapped[str] = mapped_column(String(48))
    birth_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    zodiac_sign: Mapped[ZodiacSign | None] = mapped_column(Enum(ZodiacSign), nullable=True)
    bio: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('UTC', now())"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("TIMEZONE('UTC', now())"),
    )

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
