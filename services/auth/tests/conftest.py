# ruff: noqa: E402
import json

import pytest

from httpx import AsyncClient, ASGITransport

from src import settings
from src.managers.db import DBManager
from src.models.base import Base
from src.api.dependencies import get_db
from src.db import null_pool_engine, null_pool_session_maker
from src.models import *  # noqa
from src.main import app


@pytest.fixture(scope="session", autouse=True)
def check_test_mode():
    assert settings.MODE == "TEST"


async def get_db_null_pool():
    async with DBManager(session_factory=null_pool_session_maker) as db:
        yield db


@pytest.fixture(scope="function")
async def db():
    async for db in get_db_null_pool():
        yield db


app.dependency_overrides[get_db] = get_db_null_pool


@pytest.fixture(scope="session", autouse=True)
async def setup_database(check_test_mode):
    async with null_pool_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="session", autouse=True)
async def add_users(setup_database, ac):
    users = [user for user in read_json("users")]
    for user in users:
        res = await ac.post("/v1/auth/signup", json=user)
        assert res.status_code == 201


@pytest.fixture(scope="session")
async def ac():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session")
async def get_db_users(ac, add_users):
    async with DBManager(session_factory=null_pool_session_maker) as _db:
        users = await _db.users.get_filtered()
        return [user.model_dump(mode="json") for user in users]


@pytest.fixture(scope="session")
async def get_users():
    return [user for user in read_json("users")]


@pytest.fixture(scope="session", autouse=True)
async def register_user(setup_database, ac):
    res = await ac.post(
        "/v1/auth/signup",
        json={
            "email": "test@gmail.com",
            "password": "some_pass_one_123",
            "first_name": "Test",
            "last_name": "Test",
            "birth_date": "1999-10-22",
            "bio": "What's up? I am a python backend developer. Let's colab!",
        },
    )
    assert res.status_code == 201


@pytest.fixture(scope="session")
async def authed_ac(register_user, ac):
    res = await ac.post(
        "/v1/auth/login",
        json={
            "email": "test@gmail.com",
            "password": "some_pass_one_123",
        },
    )
    assert res.status_code == 200
    assert ac.cookies.get("access_token")
    assert ac.cookies.get("refresh_token")
    yield ac


def read_json(file_name: str) -> dict:
    path = f"tests/mock_data/{file_name}.json"
    with open(path, encoding="utf-8") as file_in:
        return json.load(file_in)
