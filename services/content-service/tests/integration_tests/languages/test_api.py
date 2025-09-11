from itertools import islice

import pytest

import pycountry
from tests.utils import calculate_expected_length, get_and_validate


async def test_get_languages(ac, get_all_languages):
    per_page = 3
    for page in range(1, 10):
        data = await get_and_validate(
            ac=ac,
            url="/v1/languages",
            params={
                "page": page,
                "per_page": per_page,
            },
        )
        expected_length = calculate_expected_length(page, per_page, len(get_all_languages))
        assert len(data) == expected_length
        for item in data:
            assert isinstance(item["id"], int)
            assert isinstance(item["code"], str)


async def test_get_language(ac, get_all_languages):
    for language in islice(get_all_languages, 2):
        data = await get_and_validate(
            ac=ac,
            url=f"/v1/languages/{language['id']}",
            expect_list=False,
        )
        assert isinstance(data, dict)
        assert data["id"] == language["id"]
        assert data["code"] == language["code"]
        assert data["name"] == language["name"]


async def test_get_language_not_found(ac):
    res = await ac.get("/v1/languages/999999")
    assert res.status_code == 404
    assert "detail" in res.json()


@pytest.mark.parametrize("code", ["fa", "sw"])
async def test_add_language_valid(ac, code):
    res = await ac.post("/v1/languages", json={"code": code})
    assert res.status_code == 201

    language_id = res.json()["data"]["id"]
    added_lang = await get_and_validate(
        ac=ac,
        url=f"/v1/languages/{language_id}",
        expect_list=False,
    )
    assert isinstance(added_lang, dict)
    assert added_lang["id"] == language_id
    assert added_lang["code"] == code
    assert added_lang["name"] == pycountry.languages.get(alpha_2=code).name


@pytest.mark.parametrize("code", ["??", "gg"])
async def test_add_language_invalid(ac, code):
    res = await ac.post("/v1/languages", json={"code": code})
    assert res.status_code == 422
    assert "detail" in res.json()


async def test_add_language_on_conflict(ac, get_all_languages):
    for lang in islice(get_all_languages, 2):
        res = await ac.post("/v1/languages", json={"code": lang["code"]})
        assert res.status_code == 409
        assert "detail" in res.json()


async def test_delete_language(ac, created_languages):
    for language_id in islice(created_languages, 2):
        assert (await ac.get(f"/v1/languages/{language_id['id']}")).status_code == 200
        assert (await ac.delete(f"/v1/languages/{language_id['id']}")).status_code == 204
        assert (await ac.get(f"/v1/languages/{language_id['id']}")).status_code == 404
