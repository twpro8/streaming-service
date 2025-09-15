import pytest
from uuid_extensions import uuid7str

from src.main import app
from src.api.dependencies import get_current_user_id
from tests.utils import get_and_validate, calculate_expected_rating


users_ratings = {
    "movie": {},
    "show": {},
}


@pytest.mark.order(3)
@pytest.mark.parametrize("content_type", ("movie", "show"))
@pytest.mark.parametrize("value", (4.5, 7.5, 4.5, 8.5, 4.5, 9.5))
async def test_add_rating_valid(ac, get_all_movies, get_all_shows, content_type, value):
    user_id = uuid7str()
    app.dependency_overrides[get_current_user_id] = lambda: user_id

    if content_type == "movie":
        content_id = get_all_movies[0]["id"]
    else:
        content_id = get_all_shows[0]["id"]

    res = await ac.post(
        "/v1/ratings",
        json={
            "content_id": content_id,
            "content_type": content_type,
            "value": value,
        },
    )
    assert res.status_code == 200

    users_ratings[content_type][user_id] = value
    expected_avg = calculate_expected_rating(users_ratings[content_type])

    content = await get_and_validate(
        ac=ac,
        url=f"/v1/{content_type}s/{content_id}",
        expect_list=False,
    )
    assert content["rating"] == expected_avg


@pytest.mark.parametrize("content_type", ("movie", "show"))
@pytest.mark.parametrize(
    "field, value",
    [
        ("value", 0.0),
        ("value", 11.0),
        ("content_type", "unknown"),
    ],
)
async def test_add_rating_invalid(
    ac,
    get_all_movies,
    get_all_shows,
    content_type,
    field,
    value,
):
    if content_type == "movie":
        content_id = get_all_movies[0]["id"]
    else:
        content_id = get_all_shows[0]["id"]

    req_body = (
        {
            "content_id": content_id,
            "content_type": content_type,
            "value": 7.0,
            field: value,
        },
    )
    res = await ac.post(
        "/v1/ratings",
        json=req_body,
    )
    assert res.status_code == 422
    assert "detail" in res.json()


@pytest.mark.parametrize("content_type", ["movie", "show"])
async def test_add_rating_content_not_found(ac, content_type):
    res = await ac.post(
        "/v1/ratings",
        json={
            "content_id": uuid7str(),
            "content_type": content_type,
            "value": 1.0,
        },
    )
    assert res.status_code == 404
    assert "detail" in res.json()
