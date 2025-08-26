from pydantic import BaseModel
from sqlalchemy import insert
from sqlalchemy.exc import IntegrityError

from src.exceptions import DirectorAlreadyExistsException
from src.models.directors import DirectorORM
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import DirectorDataMapper


class DirectorRepository(BaseRepository):
    model = DirectorORM
    mapper = DirectorDataMapper

    async def add_director(self, data: BaseModel):
        stmt = insert(self.model).values(**data.model_dump()).returning(self.model.id)
        res = await self.session.execute(stmt)
        return res.scalars().one()

    async def update_director(self, director_id: int, data: BaseModel, exclude_unset: bool = False) -> None:
        try:
            await self.update(id=director_id, data=data, exclude_unset=exclude_unset)
        except IntegrityError as e:
            raise DirectorAlreadyExistsException from e
