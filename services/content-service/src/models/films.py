from datetime import datetime

from sqlalchemy import String, DECIMAL
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class FilmORM(Base):
    __tablename__ = "films"
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(512))
    director: Mapped[str] = mapped_column(String(255))
    release_year: Mapped[datetime]
    rating: Mapped[float] = mapped_column(DECIMAL(3, 1))
    duration: Mapped[int]
    file_id: Mapped[int]
    cover_id: Mapped[int]
