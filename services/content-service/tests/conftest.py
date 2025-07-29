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
from src.schemas.films import FilmAddDTO
from src.schemas.series import SeriesAddRequestDTO


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

    films_data = [FilmAddDTO.model_validate(f) for f in read_json("films")]
    series_data = [SeriesAddRequestDTO.model_validate(s) for s in read_json("series")]

    async with DBManager(session_factory=null_pool_session_maker) as db_:
        await db_.films.add_bulk(films_data)
        await db_.series.add_bulk(series_data)
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


def read_json(file_name: str) -> dict:
    path = f"tests/mock_data/{file_name}.json"
    with open(path, encoding="utf-8") as file_in:
        return json.load(file_in)
