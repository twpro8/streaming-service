from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base, int_pk, str_2, str_64


class LanguageORM(Base):
    """
    code: ISO 639-1 (example: "en")
    name: full country name in English
    """

    __tablename__ = "languages"

    id: Mapped[int_pk]
    code: Mapped[str_2] = mapped_column(unique=True, index=True)
    name: Mapped[str_64] = mapped_column(unique=True)

    def __repr__(self):
        return f"<LanguageORM(id={self.id!r}, code={self.code!r}, name={self.name!r})>"
