from pydantic import BaseModel
from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError

from src.exceptions import CountryAlreadyExistsException
from src.models import CountryORM
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import CountryDataMapper


class CountryRepository(BaseRepository):
    model = CountryORM
    mapper = CountryDataMapper

    async def add_country(self, data: BaseModel) -> int:
        stmt = insert(self.model).values(**data.model_dump()).returning(self.model.id)
        try:
            res = await self.session.execute(stmt)
        except IntegrityError as e:
            raise CountryAlreadyExistsException from e
        return res.scalars().one()

    async def update_country(
        self,
        country_id: int,
        data: BaseModel,
        exclude_unset: bool = False,
    ):
        try:
            await self.update(id=country_id, data=data, exclude_unset=exclude_unset)
        except IntegrityError as e:
            raise CountryAlreadyExistsException from e
