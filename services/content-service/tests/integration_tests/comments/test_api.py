from uuid import UUID, uuid4

import pytest

from src.schemas.pydantic_types import ContentType


prefix = "/comments"
random_uuid = str(uuid4())
valid_film_uuid = ("36eea251-89ef-454a-892c-ed559b5ae496", "2a8513f3-f255-4040-aaa6-971974b1f069")
valid_series_uuid = ("bf5315e1-fdfc-4af3-b18c-1ccc83892797", "ef66e5c2-0931-4c43-bb6d-bb2b2ec3c9c4")
comments: list[UUID] = []


@pytest.mark.parametrize(
    "content_id, content_type, comment_body, status_code, extra",
    [
        # Valid data
        (valid_film_uuid[0], ContentType.film, "Valid Comment", 201, {}),
        (valid_film_uuid[0], ContentType.film, "Valid Comment", 201, {}),
        (valid_film_uuid[0], ContentType.film, "Valid Comment", 201, {}),
        (valid_film_uuid[0], ContentType.film, "Valid Comment", 201, {}),
        (valid_film_uuid[0], ContentType.film, "Valid Comment", 201, {}),
        (valid_film_uuid[1], ContentType.film, "Valid Comment", 201, {}),
        (valid_film_uuid[1], ContentType.film, "Valid Comment", 201, {}),
        (valid_film_uuid[1], ContentType.film, "Valid Comment", 201, {}),
        (valid_film_uuid[1], ContentType.film, "Valid Comment", 201, {}),
        (valid_film_uuid[1], ContentType.film, "Valid Comment", 201, {}),
        (valid_series_uuid[0], ContentType.series, "Valid Comment", 201, {}),
        (valid_series_uuid[0], ContentType.series, "Valid Comment", 201, {}),
        (valid_series_uuid[0], ContentType.series, "Valid Comment", 201, {}),
        (valid_series_uuid[0], ContentType.series, "Valid Comment", 201, {}),
        (valid_series_uuid[0], ContentType.series, "Valid Comment", 201, {}),
        (valid_series_uuid[1], ContentType.series, "Valid Comment", 201, {}),
        (valid_series_uuid[1], ContentType.series, "Valid Comment", 201, {}),
        (valid_series_uuid[1], ContentType.series, "Valid Comment", 201, {}),
        (valid_series_uuid[1], ContentType.series, "Valid Comment", 201, {}),
        (valid_series_uuid[1], ContentType.series, "Valid Comment", 201, {}),
        # Content does not exist
        (random_uuid, ContentType.film, "Comment text", 404, {}),
        (random_uuid, ContentType.series, "Comment text", 404, {}),
        (random_uuid, ContentType.film, "Comment text", 404, {}),
        (random_uuid, ContentType.series, "Comment text", 404, {}),
        # Invalid content type
        (valid_film_uuid[0], 1, "Valid Comment", 422, {}),
        (valid_film_uuid[0], "", "Valid Comment", 422, {}),
        (valid_film_uuid[0], [], "Valid Comment", 422, {}),
        (valid_film_uuid[0], {}, "Valid Comment", 422, {}),
        (valid_film_uuid[0], True, "Valid Comment", 422, {}),
        (valid_film_uuid[0], "something", "Valid Comment", 422, {}),
        (valid_film_uuid[0], "something" * 100, "Valid Comment", 422, {}),
        # Invalid comment text
        (valid_film_uuid[0], ContentType.film, 1, 422, {}),
        (valid_film_uuid[0], ContentType.film, "", 422, {}),
        (valid_film_uuid[0], ContentType.film, "C" * 256, 422, {}),
        # Invalid UUID
        (1, ContentType.film, "Valid Comment", 422, {}),
        ([], ContentType.film, "Valid Comment", 422, {}),
        ({}, ContentType.film, "Valid Comment", 422, {}),
        (True, ContentType.film, "Valid Comment", 422, {}),
        ("uuid-is-not-valid", ContentType.film, "Valid Comment", 422, {}),
        # Extra
        (valid_film_uuid[0], ContentType.film, "Valid Comment", 422, {"Unknown": 1}),
        (valid_series_uuid[0], ContentType.series, "Valid Comment", 422, {"Unknown": 1}),
    ],
)
async def test_add_comment(
    ac,
    content_id,
    content_type,
    comment_body,
    status_code,
    extra,
):
    request_body = {
        "content_id": content_id,
        "content_type": content_type,
        "comment": comment_body,
    } | extra
    res = await ac.post(url=prefix, json=request_body)
    assert res.status_code == status_code

    if status_code == 201:
        assert res.json()["status"] == "ok"

        data = res.json()["data"]
        assert isinstance(data, dict)

        exact_id = "film_id" if content_type == ContentType.film else "series_id"

        assert data[exact_id] == content_id
        assert data["comment"] == comment_body
        assert data["id"] is not None
        assert data["created_at"] is not None

        comments.append(data["id"])


@pytest.mark.parametrize(
    "content_id, content_type, query_params, targen_length, status_code",
    [
        # Valid data
        (valid_film_uuid[0], ContentType.film, {"page": 1, "per_page": 3}, 3, 200),
        (valid_film_uuid[0], ContentType.film, {"page": 2, "per_page": 3}, 2, 200),
        (valid_film_uuid[0], ContentType.film, {"page": 3, "per_page": 3}, 0, 200),
        (valid_film_uuid[1], ContentType.film, {"page": 1, "per_page": 3}, 3, 200),
        (valid_film_uuid[1], ContentType.film, {"page": 2, "per_page": 3}, 2, 200),
        (valid_film_uuid[1], ContentType.film, {"page": 3, "per_page": 3}, 0, 200),
        (valid_series_uuid[0], ContentType.series, {"page": 1, "per_page": 3}, 3, 200),
        (valid_series_uuid[0], ContentType.series, {"page": 2, "per_page": 3}, 2, 200),
        (valid_series_uuid[0], ContentType.series, {"page": 3, "per_page": 3}, 0, 200),
        (valid_series_uuid[1], ContentType.series, {"page": 1, "per_page": 3}, 3, 200),
        (valid_series_uuid[1], ContentType.series, {"page": 2, "per_page": 3}, 2, 200),
        (valid_series_uuid[1], ContentType.series, {"page": 3, "per_page": 3}, 0, 200),
        (valid_film_uuid[0], ContentType.film, {}, 5, 200),
        (valid_film_uuid[1], ContentType.film, {}, 5, 200),
        (valid_series_uuid[0], ContentType.series, {}, 5, 200),
        (valid_series_uuid[1], ContentType.series, {}, 5, 200),
        # Invalid pagination params
        (valid_film_uuid[0], ContentType.film, {"page": -1, "per_page": 5}, 5, 422),
        (valid_film_uuid[0], ContentType.film, {"page": 10 * 25, "per_page": -1}, 5, 422),
        (valid_film_uuid[0], ContentType.film, {"page": 1, "per_page": -1}, 5, 422),
        (valid_film_uuid[0], ContentType.film, {"page": 1, "per_page": 10 * 25}, 5, 422),
        (valid_film_uuid[0], ContentType.film, {"page": True, "per_page": 5}, 5, 422),
        (valid_film_uuid[0], ContentType.film, {"page": 1, "per_page": True}, 5, 422),
        (valid_film_uuid[0], ContentType.film, {"page": {}, "per_page": 5}, 5, 422),
        (valid_film_uuid[0], ContentType.film, {"page": 1, "per_page": {}}, 5, 422),
        (random_uuid, ContentType.film, {}, 0, 200),  # no data found - returns empty list
        # Invalid uuid
        ("uuid-is-not-valid", ContentType.film, {}, 0, 422),
        # Invalid content type
        (random_uuid, "invalid content type", {}, 0, 422),
        (random_uuid, True, {}, 0, 422),
        (random_uuid, "", {}, 0, 422),
        (random_uuid, 1, {}, 0, 422),
        (random_uuid, [], {}, 0, 422),
        (random_uuid, {}, {}, 0, 422),
    ],
)
async def test_get_comments(
    ac,
    content_id,
    content_type,
    query_params,
    targen_length,
    status_code,
):
    query_params = {
        "content_id": content_id,
        "content_type": content_type,
        **query_params,
    }
    res = await ac.get(url=prefix, params=query_params)
    assert res.status_code == status_code

    if status_code == 200:
        data = res.json()["data"]
        assert isinstance(data, list)
        assert len(data) == targen_length


@pytest.mark.parametrize(
    "query_params, targen_length, status_code",
    [
        ({"page": 1, "per_page": 30}, 20, 200),
        ({"page": 1, "per_page": 8}, 8, 200),
        ({"page": 2, "per_page": 8}, 8, 200),
        ({"page": 3, "per_page": 8}, 4, 200),
        ({"page": 4, "per_page": 8}, 0, 200),
        # Invalid query params
        ({"page": -1, "per_page": 5}, 5, 422),
        ({"page": 10 * 25, "per_page": -1}, 5, 422),
        ({"page": 1, "per_page": -1}, 5, 422),
        ({"page": 1, "per_page": 10 * 25}, 5, 422),
        ({"page": True, "per_page": 5}, 5, 422),
        ({"page": 1, "per_page": True}, 5, 422),
        ({"page": {}, "per_page": 5}, 5, 422),
        ({"page": 1, "per_page": {}}, 5, 422),
    ],
)
async def test_get_user_comments(ac, query_params, targen_length, status_code):
    res = await ac.get(url="%s/user" % prefix, params=query_params)
    assert res.status_code == status_code

    if status_code == 200:
        data = res.json()["data"]
        assert isinstance(data, list)
        assert len(data) == targen_length


@pytest.mark.parametrize(
    "comment_body, status_code, extra",
    [
        ("Comment Updated", 200, {}),
        # Invalid comment
        (1, 422, {}),
        ("", 422, {}),
        ("C" * 256, 422, {}),
        # Extra
        ("Valid Comment", 422, {"Unknown": 1}),
    ],
)
async def test_update_comment(ac, comment_body, status_code, extra):
    request_body = {"comment": comment_body} | extra

    res = await ac.put(url=f"%s/{comments[0]}" % prefix, json=request_body)
    assert res.status_code == status_code

    if status_code == 200:
        res = await ac.get(url=f"%s/{comments[0]}" % prefix)
        assert res.status_code == 200

        data = res.json()["data"]

        assert isinstance(data, dict)
        assert data["id"] == comments[0]
        assert data["comment"] == comment_body


async def test_delete_comment(ac):
    for i in range(5):
        assert (await ac.get(url=f"%s/{comments[i]}" % prefix)).status_code == 200
        assert (await ac.delete(url=f"%s/{comments[i]}" % prefix)).status_code == 204
        assert (await ac.get(url=f"%s/{comments[i]}" % prefix)).status_code == 404
