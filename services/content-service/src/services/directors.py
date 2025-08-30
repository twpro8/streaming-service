from uuid import UUID, uuid4

from pydantic import BaseModel

from src.exceptions import DirectorNotFoundException, DirectorAlreadyExistsException
from src.schemas.directors import DirectorAddDTO, DirectorPatchDTO, DirectorAddRequestDTO
from src.services.base import BaseService


class DirectorService(BaseService):
    async def get_directors(self) -> list[BaseModel]:
        return await self.db.directors.get_filtered()

    async def get_director(self, director_id: UUID) -> BaseModel:
        director = await self.db.directors.get_one_or_none(id=director_id)
        if director is None:
            raise DirectorNotFoundException
        return director

    async def add_director(self, director_data: DirectorAddRequestDTO) -> UUID:
        director_id = uuid4()
        _director_data = DirectorAddDTO(
            id=director_id,
            **director_data.model_dump(),
        )
        try:
            await self.db.directors.add_director(_director_data)
        except DirectorAlreadyExistsException:
            raise
        await self.db.commit()
        return director_id

    async def update_director(self, director_id: UUID, director_data: DirectorPatchDTO) -> None:
        try:
            await self.db.directors.update_director(
                director_id=director_id,
                data=director_data,
                exclude_unset=True,
            )
        except DirectorAlreadyExistsException:
            raise
        await self.db.commit()

    async def delete_director(self, director_id: UUID) -> None:
        await self.db.directors.delete(id=director_id)
        await self.db.commit()
