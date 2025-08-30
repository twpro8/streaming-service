from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class LanguageORM(Base):
    """
    code: ISO 639-1 (example: "en")
    name: full country name in English
    """

    __tablename__ = "languages"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(2), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(64), unique=True)

    def __repr__(self):
        return f"<LanguageORM(id={self.id!r}, code={self.code!r}, name={self.name!r})>"
