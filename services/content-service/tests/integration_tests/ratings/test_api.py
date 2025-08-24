from uuid import uuid4
from decimal import Decimal, ROUND_HALF_UP

import pytest

from src.main import app
from src.api.dependencies import get_current_user_id


users_ratings = {
    "film": {},
    "series": {},
}


def calculate_expected_rating(ratings: dict[int, float]) -> str:
    avg = sum(ratings.values()) / len(ratings)
    return str(Decimal(str(avg)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))


@pytest.mark.order(3)
@pytest.mark.parametrize("content_type", ("film", "series"))
@pytest.mark.parametrize(
    "user_id, val",
    (
        (1, 4.5),
        (1, 7.5),
        (2, 4.5),
        (2, 8.5),
        (3, 4.5),
        (3, 9.5),
    ),
)
async def test_add_film_rating_valid(ac, get_all_films, get_all_series, user_id, content_type, val):
    app.dependency_overrides[get_current_user_id] = lambda: user_id  # noqa

    content_id = get_all_films[0]["id"] if content_type == "film" else get_all_series[0]["id"]

    res = await ac.post(
        "/v1/ratings",
        json={
            "content_id": str(content_id),
            "content_type": content_type,
            "value": val,
        },
    )

    assert res.status_code == 200

    users_ratings[content_type][user_id] = val
    expected_avg = calculate_expected_rating(users_ratings[content_type])

    endpoint = "/v1/films" if content_type == "film" else "/v1/series"
    res = await ac.get(f"{endpoint}/{content_id}")
    assert res.status_code == 200

    data = res.json()["data"]
    assert data["rating"] == expected_avg


@pytest.mark.parametrize(
    "field, value",
    [
        ("value", 0.0),
        ("value", 11.0),
        ("content_type", "unknown"),
    ],
)
async def test_add_rating_invalid(ac, get_all_films, field, value):
    film_id = str(get_all_films[0]["id"])
    req_body = (
        {
            "content_id": film_id,
            "content_type": "film",
            "value": 7.0,
            field: value,
        },
    )

    res = await ac.post(
        "/v1/ratings",
        json=req_body,
    )

    assert res.status_code == 422
    data = res.json()
    assert "detail" in data


@pytest.mark.parametrize("content_type", ["film", "series"])
async def test_add_rating_not_found(ac, content_type):
    content_id = str(uuid4())
    res = await ac.post(
        "/v1/ratings",
        json={
            "content_id": content_id,
            "content_type": content_type,
            "value": 1.0,
        },
    )
    assert res.status_code == 404
    data = res.json()
    assert "detail" in data
