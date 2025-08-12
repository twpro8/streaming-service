from typing import Any, AsyncGenerator

import pytest

from httpx import AsyncClient, ASGITransport

from src.config import settings
from src.api.dependencies import get_db, get_admin, get_current_user_id
from src.db import null_pool_engine, null_pool_session_maker, DBManager
from src.models.base import Base
from src.models import *  # noqa
from src.main import app
from src.schemas.episodes import EpisodeDTO
from src.schemas.films import FilmDTO
from src.schemas.genres import GenreDTO, FilmGenreDTO, SeriesGenreDTO
from src.schemas.seasons import SeasonDTO
from src.schemas.series import SeriesDTO
from tests.utils import read_json


@pytest.fixture(scope="session", autouse=True)
def check_test_mode():
    assert settings.MODE == "TEST"


async def get_db_null_pool() -> AsyncGenerator[Any, Any]:
    async with DBManager(session_factory=null_pool_session_maker) as db:
        yield db


@pytest.fixture(scope="function")
async def db() -> AsyncGenerator[Any, Any]:
    async for db in get_db_null_pool():
        yield db


app.dependency_overrides[get_db] = get_db_null_pool  # noqa
app.dependency_overrides[get_admin] = lambda: None  # noqa
app.dependency_overrides[get_current_user_id] = lambda: 1  # The number is a user_id | # noqa


@pytest.fixture(scope="session", autouse=True)
async def setup_database(check_test_mode):
    async with null_pool_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    films_data = [FilmDTO.model_validate(f) for f in read_json("films")]
    series_data = [SeriesDTO.model_validate(s) for s in read_json("series")]
    seasons_data = [SeasonDTO.model_validate(s) for s in read_json("seasons")]
    episodes_data = [EpisodeDTO.model_validate(e) for e in read_json("episodes")]
    genres_data = [GenreDTO.model_validate(g) for g in read_json("genres")]
    films_genres_data = [FilmGenreDTO.model_validate(fg) for fg in read_json("films_genres")]
    series_genres_data = [SeriesGenreDTO.model_validate(sg) for sg in read_json("series_genres")]

    async with DBManager(session_factory=null_pool_session_maker) as db_:
        await db_.films.add_bulk(films_data)
        await db_.series.add_bulk(series_data)
        await db_.seasons.add_bulk(seasons_data)
        await db_.episodes.add_bulk(episodes_data)
        await db_.genres.add_bulk(genres_data)
        await db_.films_genres.add_bulk(films_genres_data)
        await db_.series_genres.add_bulk(series_genres_data)
        await db_.commit()


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, Any]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session")
async def get_series_ids():
    data = read_json("series")
    return [series_id["id"] for series_id in data]
