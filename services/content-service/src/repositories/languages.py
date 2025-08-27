from pydantic import BaseModel
from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError

from src.exceptions import LanguageAlreadyExistsException
from src.models import LanguageORM
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import LanguageDataMapper


class LanguageRepository(BaseRepository):
    model = LanguageORM
    mapper = LanguageDataMapper

    async def add_language(self, data: BaseModel) -> int:
        stmt = insert(self.model).values(**data.model_dump()).returning(self.model.id)
        try:
            res = await self.session.execute(stmt)
        except IntegrityError as e:
            raise LanguageAlreadyExistsException from e
        return res.scalars().one()

    async def update_language(
        self,
        language_id: int,
        data: BaseModel,
        exclude_unset: bool = False,
    ):
        try:
            await self.update(id=language_id, data=data, exclude_unset=exclude_unset)
        except IntegrityError as e:
            raise LanguageAlreadyExistsException from e
