from uuid import uuid4
from decimal import Decimal, ROUND_HALF_UP

import pytest

from src.main import app
from src.api.dependencies import get_current_user_id
from src.schemas.pydantic_types import ContentType


users_ratings = {
    ContentType.film: {},
    ContentType.series: {},
}

content_ids = {
    ContentType.film: "36eea251-89ef-454a-892c-ed559b5ae496",
    ContentType.series: "bf5315e1-fdfc-4af3-b18c-1ccc83892797",
}


def calculate_expected_rating(ratings: dict[int, float]) -> str:
    avg = sum(ratings.values()) / len(ratings)
    return str(Decimal(str(avg)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


@pytest.mark.order(3)
@pytest.mark.parametrize(
    "user_id, value, content_type",
    [
        (1, 2, ContentType.film),
        (2, 8, ContentType.film),
        (3, 7.5, ContentType.film),
        (3, 7, ContentType.film),
        (3, 7.5, ContentType.film),
        (4, 7.5, ContentType.film),
        (5, 7.5, ContentType.film),
        (6, 7.5, ContentType.film),
        (7, 5.1, ContentType.film),
        (8, 5.1, ContentType.film),
        (9, 5.1, ContentType.film),
        (11, 4, ContentType.film),
        (12, 3, ContentType.film),
        (13, 3, ContentType.film),
        (1, 2, ContentType.series),
        (2, 8, ContentType.series),
        (3, 7.5, ContentType.series),
        (3, 7, ContentType.series),
        (3, 7.5, ContentType.series),
        (4, 7.5, ContentType.series),
        (5, 7.5, ContentType.series),
        (6, 7.5, ContentType.series),
        (7, 5.1, ContentType.series),
        (8, 5.1, ContentType.series),
        (9, 5.1, ContentType.series),
        (11, 4, ContentType.series),
        (12, 3, ContentType.series),
        (13, 3, ContentType.series),
    ],
)
async def test_valid_rating(ac, user_id, value, content_type):
    app.dependency_overrides[get_current_user_id] = lambda: user_id  # noqa

    content_id = content_ids[content_type]
    res = await ac.post(
        "/ratings",
        json={
            "content_id": content_id,
            "content_type": content_type,
            "value": value,
        },
    )

    assert res.status_code == 200

    users_ratings[content_type][user_id] = value
    expected_avg = calculate_expected_rating(users_ratings[content_type])

    endpoint = "/films" if content_type == ContentType.film else "/series"
    res = await ac.get(f"{endpoint}/{content_id}")
    assert res.status_code == 200

    data = res.json()["data"]
    assert data["rating"] == expected_avg


@pytest.mark.parametrize(
    "value, content_type",
    [
        # Invalid value
        (0, ContentType.film),
        (-1, ContentType.film),
        (True, ContentType.film),
        ("string", ContentType.film),
        (1.11, ContentType.film),
        (0, ContentType.series),
        (-1, ContentType.series),
        (True, ContentType.series),
        ("string", ContentType.series),
        (1.11, ContentType.series),
    ],
)
async def test_invalid_rating(ac, value, content_type):
    content_id = content_ids[content_type]
    res = await ac.post(
        "/ratings",
        json={
            "content_id": content_id,
            "content_type": content_type,
            "value": value,
        },
    )

    assert res.status_code == 422


@pytest.mark.parametrize("content_type", [ContentType.film, ContentType.series])
async def test_no_content(ac, content_type):
    content_id = str(uuid4())
    res = await ac.post(
        "/ratings",
        json={
            "content_id": content_id,
            "content_type": content_type,
            "value": 1.0,
        },
    )
    assert res.status_code == 404


@pytest.mark.parametrize("content_type", ["invalid-content-type", -1, 1, True])
async def test_invalid_content_type(ac, content_type):
    content_id = str(uuid4())
    res = await ac.post(
        "/ratings",
        json={
            "content_id": content_id,
            "content_type": content_type,
            "value": 1.0,
        },
    )
    assert res.status_code == 422
