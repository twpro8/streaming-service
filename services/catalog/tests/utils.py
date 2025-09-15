import json
from decimal import Decimal, ROUND_HALF_UP
from math import ceil
from typing import Any, Hashable, Callable


def pretty_print(obj):
    print(json.dumps(obj, indent=4, ensure_ascii=False))


def read_json(file_name: str) -> list[dict]:
    path = f"tests/mock_data/{file_name}.json"
    with open(path, encoding="utf-8") as file_in:
        return json.load(file_in)


async def get_and_validate(
    ac,
    url: str,
    *,
    params=None,
    expected_status=200,
    expect_list=True,
):
    res = await ac.get(url, params=params)
    assert res.status_code == expected_status
    data = res.json()["data"]
    if expect_list:
        assert isinstance(data, list)
    return data


def count_content(items, field, value):
    return sum(1 for item in items if value.strip().lower() in item[field].lower())


def calculate_expected_length(page, per_page, total_count):
    total_pages = ceil(total_count / per_page)
    if page <= total_pages:
        expected_length = min(per_page, total_count - (page - 1) * per_page)
    else:
        expected_length = 0
    return expected_length


def first_group(
    items: list[dict[str, Any]],
    group_by: str,
    n: int,
) -> list[dict[str, Any]]:
    seen: dict[Hashable, list[dict[str, Any]]] = {}
    for item in items:
        group = item[group_by]
        seen.setdefault(group, []).append(item)
        if len(seen[group]) == n:
            return seen[group]

    raise ValueError(f"No group found with {n} items")


def first_different(
    items: list[dict[str, Any]],
    attr_name: str,
    n: int,
) -> list[dict[str, Any]]:
    seen: dict[Any, dict[str, Any]] = {}
    result: list[dict[str, Any]] = []

    for item in items:
        value = item[attr_name]
        if value not in seen:
            seen[value] = item
            result.append(item)
            if len(result) == n:
                return result

    raise ValueError(f"No different {n} items found")


def next_number(
    items: list[dict[str, Any]], key: str, condition: Callable[[dict[str, Any]], bool] | None = None
) -> int:
    filtered = (item[key] for item in items if condition is None or condition(item))
    return max(filtered, default=0) + 1


def calculate_expected_rating(ratings: dict[int, float]) -> str:
    avg = sum(ratings.values()) / len(ratings)
    return str(Decimal(str(avg)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))
