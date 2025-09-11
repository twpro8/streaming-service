from itertools import islice

import pytest

import pycountry
from tests.utils import calculate_expected_length, get_and_validate


async def test_get_countries(ac, get_all_countries):
    per_page = 3
    for page in range(1, 10):
        data = await get_and_validate(
            ac=ac,
            url="/v1/countries",
            params={
                "page": page,
                "per_page": per_page,
            },
        )
        expected_length = calculate_expected_length(page, per_page, len(get_all_countries))
        assert len(data) == expected_length
        for item in data:
            assert isinstance(item["id"], int)
            assert isinstance(item["code"], str)


async def test_get_country(ac, get_all_countries):
    for country in islice(get_all_countries, 2):
        data = await get_and_validate(
            ac=ac,
            url=f"/v1/countries/{country['id']}",
            expect_list=False,
        )
        assert isinstance(data, dict)
        assert data["id"] == country["id"]
        assert data["code"] == country["code"]
        assert data["name"] == country["name"]


async def test_get_country_not_found(ac):
    res = await ac.get("/v1/countries/999999")
    assert res.status_code == 404
    assert "detail" in res.json()


@pytest.mark.parametrize("code", ["CL", "PH", "TH"])
async def test_add_country_valid(ac, code):
    res = await ac.post("/v1/countries", json={"code": code})
    assert res.status_code == 201

    country_id = res.json()["data"]["id"]
    added_country = await get_and_validate(
        ac=ac,
        url=f"/v1/countries/{country_id}",
        expect_list=False,
    )
    assert isinstance(added_country, dict)
    assert added_country["id"] == country_id
    assert added_country["code"] == code
    assert added_country["name"] == pycountry.countries.get(alpha_2=code).name


@pytest.mark.parametrize("code", ["??", "FD"])
async def test_add_country_invalid(ac, code):
    res = await ac.post("/v1/countries", json={"code": code})
    assert res.status_code == 422
    assert "detail" in res.json()


async def test_add_country_on_conflict(ac, get_all_countries):
    for country in islice(get_all_countries, 2):
        res = await ac.post("/v1/countries", json={"code": country["code"]})
        assert res.status_code == 409
        assert "detail" in res.json()


async def test_delete_country(ac, get_all_countries):
    for country_id in islice(get_all_countries, 2):
        assert (await ac.get(f"/v1/countries/{country_id['id']}")).status_code == 200
        assert (await ac.delete(f"/v1/countries/{country_id['id']}")).status_code == 204
        assert (await ac.get(f"/v1/countries/{country_id['id']}")).status_code == 404
