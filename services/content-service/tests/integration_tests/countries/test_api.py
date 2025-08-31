import pytest

import pycountry
from tests.utils import calculate_expected_length


@pytest.mark.parametrize(
    "params",
    [
        {"page": 1, "per_page": 3},
        {"page": 3, "per_page": 3},
        {"page": 4, "per_page": 3},
        {"page": 5, "per_page": 3},
        {"page": 7, "per_page": 3},
        {"page": 8, "per_page": 3},
        {"page": 15, "per_page": 3},
        {"page": 1, "per_page": 30},
    ],
)
async def test_get_countries(ac, params, get_all_countries):
    res = await ac.get("/v1/countries", params=params)
    assert res.status_code == 200

    data = res.json()["data"]

    expected_length = calculate_expected_length(
        params["page"], params["per_page"], len(get_all_countries)
    )

    assert len(data) == expected_length

    for item in data:
        assert isinstance(item["id"], int)
        assert isinstance(item["code"], str)


async def test_get_existing_country(ac, get_all_countries):
    for country in get_all_countries:
        res = await ac.get(f"/v1/countries/{country['id']}")
        assert res.status_code == 200
        lang = res.json()["data"]
        assert lang["id"] == country["id"]


async def test_get_nonexistent_country(ac):
    res = await ac.get("/v1/countries/999999")
    assert res.status_code == 404


@pytest.mark.parametrize("code", ["CL", "PH", "TH"])
async def test_add_country_valid(ac, code):
    res = await ac.post("/v1/countries", json={"code": code})
    assert res.status_code == 201
    country_id = res.json()["data"]["id"]

    res = await ac.get(f"/v1/countries/{country_id}")
    assert res.status_code == 200

    data = res.json()["data"]
    assert data["code"] == code
    assert data["name"] == pycountry.countries.get(alpha_2=code).name

    await ac.delete(f"/v1/countries/{country_id}")


@pytest.mark.parametrize("code", ["??", "FD", 1])
async def test_add_country_invalid(ac, code):
    res = await ac.post("/v1/countries", json={"code": code})
    assert res.status_code == 422
    assert "detail" in res.json()


@pytest.mark.parametrize("code", ["US", "CA"])
async def test_add_country_on_conflict(ac, code):
    res = await ac.post("/v1/countries", json={"code": code})
    assert res.status_code == 409
    detail = res.json()["detail"]
    assert "country" in detail.strip().lower()


async def test_delete_country(ac, created_countries):
    for country_id in created_countries:
        assert (await ac.get(f"/v1/countries/{country_id['id']}")).status_code == 200
        assert (await ac.delete(f"/v1/countries/{country_id['id']}")).status_code == 204
        assert (await ac.get(f"/v1/countries/{country_id['id']}")).status_code == 404
