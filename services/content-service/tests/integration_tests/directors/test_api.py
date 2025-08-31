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
    ],
)
async def test_directors_pagination(ac, page, per_page, get_all_directors):
    expected_length = calculate_expected_length(page, per_page, len(get_all_directors))
    data = await get_and_validate(ac, "/v1/directors", params={"page": page, "per_page": per_page})
    assert len(data) == expected_length


async def test_get_existing_director(ac, get_all_directors):
    for director in get_all_directors:
        data = await get_and_validate(ac, f"/v1/directors/{director['id']}", expect_list=False)
        assert isinstance(data, dict)


async def test_get_nonexistent_director(ac):
    res = await ac.get(f"/v1/directors/{uuid4()}")
    assert res.status_code == 404
    assert "detail" in res.json()


@pytest.mark.parametrize(
    "first_name, last_name, birth_date, zodiac_sign, bio",
    [
        ("John", "Smith", "1977-01-17", None, None),
        ("Lana", "Light", "1988-01-25", ZodiacSign.pisces, "Well-known director"),
    ],
)
async def test_add_director_valid(ac, first_name, last_name, birth_date, zodiac_sign, bio):
    req_body = {
        "first_name": first_name,
        "last_name": last_name,
        "birth_date": birth_date,
        "zodiac_sign": zodiac_sign,
        "bio": bio,
    }
    res = await ac.post("/v1/directors", json=req_body)
    assert res.status_code == 201

    director_id = res.json()["data"]["id"]

    director = await get_and_validate(ac, f"/v1/directors/{director_id}", expect_list=False)

    assert director["first_name"] == first_name
    assert director["last_name"] == last_name
    assert director["birth_date"] == birth_date
    assert director["zodiac_sign"] == zodiac_sign
    assert director["bio"] == bio


invalid_cases = [
    ("first_name", ["f", "f" * 50, None]),
    ("last_name", ["l", "l" * 50, None]),
    ("birth_date", ["999-01-01", "2100-01-01", "invalid-format"]),
    ("zodiac_sign", ["Rat", "Cat", "Boss"]),
    ("bio", ["b", "b" * 1025]),
    ("extra", ["Hello!"]),
]


@pytest.mark.parametrize(
    "field, invalid_value", [(field, val) for field, vals in invalid_cases for val in vals]
)
async def test_add_director_invalid(ac, field, invalid_value):
    data = {
        "first_name": "Test1",
        "last_name": "Test1",
        "birth_date": "1955-01-01",
        "zodiac_sign": ZodiacSign.pisces,
        "bio": "Likes kittens...",
        field: invalid_value,
    }
    res = await ac.post("/v1/directors", json=data)
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
        ("zodiac_sign", ZodiacSign.aquarius),
        ("zodiac_sign", ZodiacSign.capricorn),
        ("bio", "Updated bio one ... "),
        ("bio", "Updated bio two ... "),
    ],
)
async def test_update_director_valid(ac, field, value, get_all_directors):
    director_id = get_all_directors[0]["id"]

    res = await ac.patch(f"/v1/directors/{director_id}", json={field: value})
    assert res.status_code == 200

    director = await get_and_validate(ac, f"/v1/directors/{director_id}", expect_list=False)
    assert director[field] == value


@pytest.mark.parametrize(
    "field, value",
    [
        ("first_name", "f"),
        ("first_name", "f" * 50),
        ("last_name", "l"),
        ("last_name", "l" * 50),
        ("birth_date", "999-01-01"),
        ("birth_date", "2100-01-01"),
        ("zodiac_sign", "Corn dog"),
        ("bio", "b"),
        ("bio", "b" * 1025),
    ],
)
async def test_update_director_invalid(ac, field, value, get_all_directors):
    director_id = get_all_directors[0]["id"]

    res = await ac.patch(f"/v1/directors/{director_id}", json={field: value})
    assert res.status_code == 422
    assert "detail" in res.json()


async def test_delete_director(ac, get_all_directors):
    for director in get_all_directors:
        assert (await ac.get(f"/v1/directors/{director['id']}")).status_code == 200
        assert (await ac.delete(f"/v1/directors/{director['id']}")).status_code == 204
        assert (await ac.get(f"/v1/directors/{director['id']}")).status_code == 404
