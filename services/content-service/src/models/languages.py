from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class LanguageORM(Base):
    """
    code: ISO 639-1 (example: "en")
    name: full country name in English
    native_name: native full country name
    """

    __tablename__ = "languages"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(2), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    native_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=True)

    def __repr__(self):
        return (
            f"<LanguageORM(id={self.id}, code='{self.code}', "
            f"name='{self.name}', native_name='{self.native_name}')>"
        )
