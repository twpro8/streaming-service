from uuid import uuid4

import pytest

from src.enums import ZodiacSign
from tests.utils import get_and_validate, calculate_expected_length


@pytest.mark.parametrize(
    "page, per_page",
    [
        (1, 3),
        (2, 3),
        (3, 3),
        (4, 3),
        (5, 3),
    ]
)
async def test_actors_pagination(ac, page, per_page, get_all_actors):
    expected_length = calculate_expected_length(page, per_page, len(get_all_actors))
    data = await get_and_validate(ac, "/actors", params={"page": page, "per_page": per_page})
    assert len(data) == expected_length


async def test_get_existing_actor(ac, get_all_actors):
    for actor in get_all_actors:
        data = await get_and_validate(ac, f"/actors/{actor["id"]}", expect_list=False)
        assert isinstance(data, dict)


async def test_get_nonexistent_actor(ac):
    res = await ac.get(f"/actors/{uuid4()}")
    assert res.status_code == 404
    assert "detail" in res.json()


@pytest.mark.parametrize(
    "first_name, last_name, birth_date, zodiac_sign, bio",
    [
        ("John", "Smith", "1977-01-17", None, None),
        ("Lana", "Light", "1988-01-25", ZodiacSign.PISCES, "Well-known actress"),
    ]
)
async def test_add_actor_valid(ac, first_name, last_name, birth_date, zodiac_sign, bio):
    req_body = {
        "first_name": first_name,
        "last_name": last_name,
        "birth_date": birth_date,
        "zodiac_sign": zodiac_sign,
        "bio": bio,
    }
    res = await ac.post("/actors", json=req_body)
    assert res.status_code == 201

    actor_id = res.json()["data"]["id"]

    actor = await get_and_validate(ac, f"/actors/{actor_id}", expect_list=False)

    assert actor["first_name"] == first_name
    assert actor["last_name"] == last_name
    assert actor["birth_date"] == birth_date
    assert actor["zodiac_sign"] == zodiac_sign
    assert actor["bio"] == bio


invalid_cases = [
    ("first_name", ["f", "f"*50, None]),
    ("last_name", ["l", "l"*50, None]),
    ("birth_date", ["999-01-01", "2100-01-01", "invalid-format", None]),
    ("zodiac_sign", ["Rat", "Cat", "Boss"]),
    ("bio", ["b", "b"*130]),
    ("extra", ["Hello!"]),
]

@pytest.mark.parametrize(
    "field, invalid_value", [(field, val) for field, vals in invalid_cases for val in vals]
)
async def test_add_actor_invalid(ac, field, invalid_value):
    data = {
        "first_name": "Test1",
        "last_name": "Test1",
        "birth_date": "1955-01-01",
        "zodiac_sign": ZodiacSign.PISCES,
        "bio": "Likes kittens...",
        field: invalid_value,
    }
    res = await ac.post("/actors", json=data)
    assert res.status_code == 422
    assert "detail" in res.json()


@pytest.mark.parametrize(
    "field, value",
    [
        ("first_name", "Updated One"),
        ("first_name", "Updated Two"),
        ("last_name", "Updated One"),
        ("last_name", "Updated Two"),
        ("birth_date", "1959-01-01"),
        ("birth_date", "1957-01-01"),
        ("zodiac_sign", ZodiacSign.AQUARIUS),
        ("zodiac_sign", ZodiacSign.CAPRICORN),
        ("bio", "Updated bio one ... "),
        ("bio", "Updated bio two ... "),
    ]
)
async def test_update_actor_valid(ac, field, value, get_all_actors):
    actor_id = get_all_actors[0]["id"]

    res = await ac.patch(f"/actors/{actor_id}", json={field: value})
    assert res.status_code == 200

    actor = await get_and_validate(ac, f"/actors/{actor_id}", expect_list=False)
    assert actor[field] == value


@pytest.mark.parametrize(
    "field, value",
    [
        ("first_name", "f"),
        ("first_name", "f"*50),
        ("last_name", "l"),
        ("last_name", "l"*50),
        ("birth_date", "999-01-01"),
        ("birth_date", "2100-01-01"),
        ("zodiac_sign", "Corn dog"),
        ("bio", "b"),
        ("bio", "b"*130),
    ]
)
async def test_update_actor_invalid(ac, field, value, get_all_actors):
    actor_id = get_all_actors[0]["id"]

    res = await ac.patch(f"/actors/{actor_id}", json={field: value})
    assert res.status_code == 422
    assert "detail" in res.json()


async def test_delete_actor(ac, get_all_actors):
    for actor in get_all_actors:
        assert (await ac.get(f"/actors/{actor["id"]}")).status_code == 200
        assert (await ac.delete(f"/actors/{actor["id"]}")).status_code == 204
        assert (await ac.get(f"/actors/{actor["id"]}")).status_code == 404
