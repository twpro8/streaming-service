import json
from typing import Any, AsyncGenerator

import pytest

from httpx import AsyncClient, ASGITransport

from src.config import settings
from src.api.dependencies import get_db, get_admin
from src.db import null_pool_engine, null_pool_session_maker, DBManager
from src.models.base import Base
from src.models import *  # noqa
from src.main import app
from src.schemas.episodes import EpisodeDTO
from src.schemas.films import FilmDTO
from src.schemas.seasons import SeasonDTO
from src.schemas.series import SeriesDTO


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


@pytest.fixture(scope="session", autouse=True)
async def setup_database(check_test_mode):
    async with null_pool_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    films_data = [FilmDTO.model_validate(f) for f in read_json("films")]
    series_data = [SeriesDTO.model_validate(s) for s in read_json("series")]
    seasons_data = [SeasonDTO.model_validate(s) for s in read_json("seasons")]
    episodes_data = [EpisodeDTO.model_validate(e) for e in read_json("episodes")]

    async with DBManager(session_factory=null_pool_session_maker) as db_:
        await db_.films.add_bulk(films_data)
        await db_.series.add_bulk(series_data)
        await db_.seasons.add_bulk(seasons_data)
        await db_.episodes.add_bulk(episodes_data)
        await db_.commit()


@pytest.fixture(scope="session")
async def ac() -> AsyncGenerator[AsyncClient, Any]:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session")
async def get_films_ids(ac):
    res = await ac.get("/films")
    return [i["id"] for i in res.json()["data"]]


@pytest.fixture(scope="session")
async def get_series_ids(ac):
    res = await ac.get("/series")
    return [i["id"] for i in res.json()["data"]]


def pretty_print(obj):
    print(json.dumps(obj, indent=4, ensure_ascii=False))


def read_json(file_name: str) -> list[dict]:
    path = f"tests/mock_data/{file_name}.json"
    with open(path, encoding="utf-8") as file_in:
        return json.load(file_in)
