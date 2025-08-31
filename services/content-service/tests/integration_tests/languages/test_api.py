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
async def test_get_languages(ac, params, get_all_languages):
    res = await ac.get("/v1/languages", params=params)
    assert res.status_code == 200

    data = res.json()["data"]

    expected_length = calculate_expected_length(
        params["page"], params["per_page"], len(get_all_languages)
    )

    assert len(data) == expected_length

    for item in data:
        assert isinstance(item["id"], int)
        assert isinstance(item["code"], str)


async def test_get_existing_language(ac, get_all_languages):
    for language in get_all_languages:
        res = await ac.get(f"/v1/languages/{language['id']}")
        assert res.status_code == 200
        lang = res.json()["data"]
        assert lang["id"] == language["id"]


async def test_get_nonexistent_language(ac):
    res = await ac.get("/v1/languages/999999")
    assert res.status_code == 404


@pytest.mark.parametrize("code", ["fa", "sw"])
async def test_add_language_valid(ac, code):
    res = await ac.post("/v1/languages", json={"code": code})
    assert res.status_code == 201
    language_id = res.json()["data"]["id"]

    res = await ac.get(f"/v1/languages/{language_id}")
    assert res.status_code == 200

    data = res.json()["data"]
    assert data["code"] == code
    assert data["name"] == pycountry.languages.get(alpha_2=code).name

    await ac.delete(f"/v1/languages/{language_id}")


@pytest.mark.parametrize("code", ["??", "gg", 1])
async def test_add_language_invalid(ac, code):
    res = await ac.post("/v1/languages", json={"code": code})
    assert res.status_code == 422
    assert "detail" in res.json()


@pytest.mark.parametrize("code", ["en", "ru"])
async def test_add_language_on_conflict(ac, code):
    res = await ac.post("/v1/languages", json={"code": code})
    assert res.status_code == 409
    detail = res.json()["detail"]
    assert "language" in detail.strip().lower()


async def test_delete_language(ac, created_languages):
    for language_id in created_languages:
        assert (await ac.get(f"/v1/languages/{language_id['id']}")).status_code == 200
        assert (await ac.delete(f"/v1/languages/{language_id['id']}")).status_code == 204
        assert (await ac.get(f"/v1/languages/{language_id['id']}")).status_code == 404
