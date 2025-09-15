from itertools import islice

import pytest
from uuid_extensions import uuid7str

from tests.utils import get_and_validate, calculate_expected_length


@pytest.mark.order(3)
@pytest.mark.parametrize("content_type", ("movie", "show"))
async def test_get_content_comments(ac, get_all_comments, content_type):
    per_page = 2
    for page in range(1, 5):
        content_id = next(
            c["content_id"] for c in get_all_comments if c["content_type"] == content_type
        )
        all_comments = [c for c in get_all_comments if c["content_id"] == content_id]
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
async def test_get_user_comments_valid(ac, get_all_comments, current_user_id):
    per_page = 3
    for page in range(1, 5):
        all_user_comments = [c for c in get_all_comments if c["user_id"] == current_user_id]
        assert len(all_user_comments) >= 5

        expected_count = calculate_expected_length(page, per_page, len(all_user_comments))

        comments = await get_and_validate(
            ac=ac,
            url="/v1/comments/user",
            params={"page": page, "per_page": per_page},
        )
        assert len(comments) == expected_count


async def test_get_comment(ac, get_all_comments):
    for comment in islice(get_all_comments, 2):
        data = await get_and_validate(
            ac=ac,
            url=f"/v1/comments/{comment['id']}",
            expect_list=False,
        )
        assert data["id"] == comment["id"]
        assert data["user_id"] == comment["user_id"]
        assert data["content_id"] == comment["content_id"]
        assert data["content_type"] == comment["content_type"]
        assert data["created_at"] == comment["created_at"]
        assert data["updated_at"] == comment["updated_at"]


async def test_get_comment_not_found(ac):
    res = await ac.get(f"/v1/comments/{uuid7str()}")
    assert res.status_code == 404
    assert "detail" in res.json()


@pytest.mark.order(3)
@pytest.mark.parametrize(
    "content_type, text",
    (
        ("movie", "Valid comment text 1"),
        ("show", "Valid comment text 2"),
    ),
)
async def test_add_comment_valid(
    ac,
    current_user_id,
    get_all_movies,
    get_all_shows,
    content_type,
    text,
):
    if content_type == "movie":
        content_id = get_all_movies[0]["id"]
    else:
        content_id = get_all_shows[0]["id"]

    res = await ac.post(
        url="/v1/comments",
        json={
            "content_id": content_id,
            "content_type": content_type,
            "comment": text,
        },
    )
    assert res.status_code == 201

    comment_id = res.json()["data"]["id"]
    added_comment = await get_and_validate(
        ac=ac,
        url=f"/v1/comments/{comment_id}",
        expect_list=False,
    )
    assert added_comment["id"] == comment_id
    assert added_comment["user_id"] == current_user_id
    assert added_comment["content_id"] == content_id
    assert added_comment["content_type"] == content_type
    assert added_comment["comment"] == text
    assert added_comment["created_at"]
    assert added_comment["updated_at"]


@pytest.mark.order(3)
@pytest.mark.parametrize("content_type", ("movie", "show"))
@pytest.mark.parametrize(
    "field, value",
    (
        ("comment", "t"),
        ("comment", "t" * 513),
        ("content_type", "unknown"),
        ("show_id", "invalid-format"),
    ),
)
async def test_add_comment_invalid(ac, get_all_movies, get_all_shows, content_type, field, value):
    if content_type == "movie":
        content_id = get_all_movies[0]["id"]
    else:
        content_id = get_all_shows[0]["id"]

    res = await ac.post(
        url="/v1/comments",
        json={
            "content_id": content_id,
            "content_type": content_type,
            "comment": "Valid comment text",
            field: value,
        },
    )
    assert res.status_code == 422


@pytest.mark.order(3)
@pytest.mark.parametrize("content_type", ("movie", "show"))
async def test_add_comment_content_not_found(ac, content_type):
    res = await ac.post(
        url="/v1/comments",
        json={
            "content_id": uuid7str(),
            "content_type": content_type,
            "comment": "Valid comment text",
        },
    )
    assert res.status_code == 404


@pytest.mark.order(3)
async def test_update_comment_valid(ac, get_all_comments):
    comment = get_all_comments[0]
    text = "Updated comment text"

    res = await ac.put(f"/v1/comments/{comment['id']}", json={"comment": text})
    assert res.status_code == 200

    updated_comment = await get_and_validate(
        ac=ac,
        url=f"/v1/comments/{comment['id']}",
        expect_list=False,
    )
    assert updated_comment["id"] == comment["id"]
    assert updated_comment["user_id"] == comment["user_id"]
    assert updated_comment["content_id"] == comment["content_id"]
    assert updated_comment["content_type"] == comment["content_type"]
    assert updated_comment["comment"] == text
    assert updated_comment["created_at"] == comment["created_at"]
    assert updated_comment["updated_at"] != comment["updated_at"]


@pytest.mark.order(3)
@pytest.mark.parametrize(
    "field, value",
    (
        ("comment", "t"),
        ("comment", "t" * 513),
        ("extra", "unknown"),
    ),
)
async def test_update_comment_invalid(ac, get_all_comments, field, value):
    comment_id = get_all_comments[0]["id"]
    res = await ac.put(
        f"/v1/comments/{comment_id}",
        json={
            "comment": "Valid comment text",
            field: value,
        },
    )
    assert res.status_code == 422
    assert "detail" in res.json()


async def test_update_comment_not_found(ac):
    res = await ac.put(f"/v1/comments/{uuid7str()}", json={"comment": "Valid comment text"})
    assert res.status_code == 404
    assert "detail" in res.json()


@pytest.mark.order(3)
async def test_delete_comment(ac, get_all_comments):
    for comment in islice(get_all_comments, 2):
        assert (await ac.get(url=f"/v1/comments/{comment['id']}")).status_code == 200
        assert (await ac.delete(url=f"/v1/comments/{comment['id']}")).status_code == 204
        assert (await ac.get(url=f"/v1/comments/{comment['id']}")).status_code == 404
