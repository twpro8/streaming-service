from uuid import UUID

from pydantic import BaseModel
from uuid_extensions import uuid7

from src.exceptions import DirectorNotFoundException, DirectorAlreadyExistsException
from src.schemas.directors import DirectorAddDTO, DirectorPatchDTO, DirectorAddRequestDTO
from src.services.base import BaseService


class DirectorService(BaseService):
    async def get_directors(self, page: int, per_page: int) -> list[BaseModel]:
        directors = await self.db.directors.get_filtered(page=page, per_page=per_page)
        return directors

    async def get_director(self, director_id: UUID) -> BaseModel:
        director = await self.db.directors.get_one_or_none(id=director_id)
        if director is None:
            raise DirectorNotFoundException
        return director

    async def add_director(self, director_data: DirectorAddRequestDTO) -> UUID:
        director_id = uuid7()
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
        except (DirectorNotFoundException, DirectorAlreadyExistsException):
            raise
        await self.db.commit()

    async def delete_director(self, director_id: UUID) -> None:
        await self.db.directors.delete(id=director_id)
        await self.db.commit()
