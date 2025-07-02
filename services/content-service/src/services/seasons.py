from uuid import UUID

from src.exceptions import (
    SeasonNotFoundException,
    ObjectAlreadyExistsException,
    SeasonAlreadyExistsException,
    SeriesNotFoundException,
)
from src.schemas.seasons import SeasonAddRequestDTO, SeasonPatchRequestDTO, SeasonAddDTO
from src.services.base import BaseService


class SeasonService(BaseService):
    async def get_seasons(self, series_id: UUID, pagination):
        seasons = await self.db.seasons.get_filtered(
            series_id=series_id, page=pagination.page, per_page=pagination.per_page
        )
        return seasons

    async def add_season(self, series_id: UUID, season_data: SeasonAddRequestDTO):
        if not await self.check_series_exists(id=series_id):
            raise SeriesNotFoundException

        new_data = SeasonAddDTO(
            series_id=series_id,
            **season_data.model_dump(),
        )
        try:
            season = await self.db.seasons.add(new_data)
        except ObjectAlreadyExistsException:
            raise SeasonAlreadyExistsException
        await self.db.commit()
        return season

    async def update_season(
        self, season_data: SeasonPatchRequestDTO, series_id: UUID, season_id: UUID
    ):
        if not await self.check_series_exists(id=series_id):
            raise SeriesNotFoundException
        if not await self.check_season_exists(id=season_id):
            raise SeasonNotFoundException

        await self.db.seasons.update(
            data=season_data,
            exclude_unset=True,
            id=season_id,
            series_id=series_id,
        )
        await self.db.commit()

    async def delete_season(self, series_id: UUID, season_id: UUID):
        await self.db.seasons.delete(id=season_id, series_id=series_id)
        await self.db.commit()
