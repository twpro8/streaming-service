from uuid import uuid4

import pytest

from tests.utils import get_and_validate, calculate_expected_length


@pytest.mark.order(3)
@pytest.mark.parametrize("content_type, id_key", (("film", "film_id"), ("series", "series_id")))
@pytest.mark.parametrize("page, per_page", ((1, 2), (2, 2), (3, 2), (4, 2)))
async def test_get_content_comments(ac, get_all_comments, content_type, id_key, page, per_page):
    content_id = next(c[id_key] for c in get_all_comments if c.get(id_key, None))
    all_comments = [c for c in get_all_comments if c.get(id_key, None) == content_id]
    assert len(all_comments) >= 5

    expected_count = calculate_expected_length(page, per_page, len(all_comments))

    comments = await get_and_validate(
        ac=ac,
        url="/v1/comments",
        params={
            "page": page,
            "per_page": per_page,
            "content_id": content_id,
            "content_type": content_type,
        },
    )
    assert len(comments) == expected_count


@pytest.mark.order(3)
@pytest.mark.parametrize("page, per_page", ((1, 3), (2, 3), (3, 3), (4, 3)))
async def test_get_user_comments_valid(ac, get_all_comments, current_user_id, page, per_page):
    all_user_comments = [c for c in get_all_comments if c["user_id"] == current_user_id]
    assert len(all_user_comments) >= 5

    expected_count = calculate_expected_length(
        page=page,
        per_page=per_page,
        total_count=len(all_user_comments),
    )

    comments = await get_and_validate(
        ac=ac, url="/v1/comments/user", params={"page": page, "per_page": per_page}
    )
    assert len(comments) == expected_count


@pytest.mark.order(3)
@pytest.mark.parametrize("text", ("Valid comment text 1", "Valid comment text 2"))
async def test_add_film_comment_valid(ac, get_all_films, text):
    film_id = str(get_all_films[0]["id"])

    res = await ac.post(
        url="/v1/comments",
        json={
            "content_id": film_id,
            "content_type": "film",
            "comment": text,
        },
    )
    assert res.status_code == 201

    comment_id = res.json()["data"]["id"]

    comment = await get_and_validate(ac, f"/v1/comments/{comment_id}", expect_list=False)

    assert comment["id"] == comment_id
    assert comment["comment"] == text
    assert comment["film_id"] == film_id
    assert comment["created_at"] is not None


@pytest.mark.order(3)
@pytest.mark.parametrize("text", ("Valid comment text 1", "Valid comment text 2"))
async def test_add_series_comment_valid(ac, get_all_series, text):
    series_id = str(get_all_series[0]["id"])

    res = await ac.post(
        url="/v1/comments",
        json={
            "content_id": series_id,
            "content_type": "series",
            "comment": text,
        },
    )
    assert res.status_code == 201

    comment_id = res.json()["data"]["id"]

    comment = await get_and_validate(ac, f"/v1/comments/{comment_id}", expect_list=False)

    assert comment["id"] == comment_id
    assert comment["comment"] == text
    assert comment["series_id"] == series_id
    assert comment["created_at"] is not None


@pytest.mark.order(3)
@pytest.mark.parametrize(
    "field, value",
    (
        ("comment", "t"),
        ("comment", "t" * 256),
        ("content_type", "unknown"),
        ("series_id", "invalid-format"),
    ),
)
async def test_add_comment_invalid(ac, get_all_films, field, value):
    film_id = str(get_all_films[0]["id"])
    res = await ac.post(
        url="/v1/comments",
        json={
            "content_id": film_id,
            "content_type": "film",
            "comment": "Valid comment text",
            field: value,
        },
    )
    assert res.status_code == 422


@pytest.mark.order(3)
@pytest.mark.parametrize("content_type", ("film", "series"))
async def test_add_comment_content_not_found(ac, content_type):
    res = await ac.post(
        url="/v1/comments",
        json={
            "content_id": str(uuid4()),
            "content_type": content_type,
            "comment": "Valid comment text",
        },
    )
    assert res.status_code == 404


@pytest.mark.order(3)
async def test_update_comment_valid(ac, get_all_comments):
    comment_id = str(get_all_comments[0]["id"])

    res = await ac.put(f"/v1/comments/{comment_id}", json={"comment": "Updated comment text"})
    assert res.status_code == 200

    comment = await get_and_validate(ac, f"/v1/comments/{comment_id}", expect_list=False)
    assert comment["comment"] == "Updated comment text"


@pytest.mark.order(3)
@pytest.mark.parametrize(
    "field, value",
    (
        ("comment", "t"),
        ("comment", "t" * 256),
        ("extra", "unknown"),
    ),
)
async def test_update_comment_invalid(ac, get_all_comments, field, value):
    comment_id = str(get_all_comments[0]["id"])
    res = await ac.put(
        f"/v1/comments/{comment_id}",
        json={
            "comment": "Valid comment text",
            field: value,
        },
    )
    assert res.status_code == 422


@pytest.mark.order(3)
async def test_delete_comment(ac, get_all_comments):
    for comment in get_all_comments[:5]:
        assert (await ac.get(url=f"/v1/comments/{comment['id']}")).status_code == 200
        assert (await ac.delete(url=f"/v1/comments/{comment['id']}")).status_code == 204
        assert (await ac.get(url=f"/v1/comments/{comment['id']}")).status_code == 404
