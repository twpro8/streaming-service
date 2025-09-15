from uuid import UUID

from uuid_extensions import uuid7

from src.exceptions import (
    SeasonNotFoundException,
    ShowNotFoundException,
    SeasonAlreadyExistsException,
)
from src.schemas.seasons import SeasonPatchRequestDTO, SeasonAddDTO, SeasonAddRequestDTO
from src.services.base import BaseService


class SeasonService(BaseService):
    async def get_seasons(self, show_id: UUID | None, page: int, per_page: int):
        seasons = await self.db.seasons.get_filtered(
            show_id=show_id,
            page=page,
            per_page=per_page,
        )
        return seasons

    async def get_season(self, season_id: UUID):
        season = await self.db.seasons.get_one_or_none(id=season_id)
        if not season:
            raise SeasonNotFoundException
        return season

    async def add_season(self, season_data: SeasonAddRequestDTO) -> UUID:
        if not await self.check_show_exists(id=season_data.show_id):
            raise ShowNotFoundException

        season_id = uuid7()
        _season_data = SeasonAddDTO(id=season_id, **season_data.model_dump())

        try:
            await self.db.seasons.add_season(data=_season_data)
        except SeasonAlreadyExistsException:
            raise

        await self.db.commit()
        return season_id

    async def update_season(self, season_data: SeasonPatchRequestDTO, season_id: UUID):
        try:
            await self.db.seasons.update_season(
                season_id=season_id,
                data=season_data,
                exclude_unset=True,
            )
        except (SeasonNotFoundException, SeasonAlreadyExistsException):
            raise
        await self.db.commit()

    async def delete_season(self, season_id: UUID):
        await self.db.seasons.delete(id=season_id)
        await self.db.commit()
