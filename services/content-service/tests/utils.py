import json


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


def count_films(films, field, value):
    return sum(1 for film in films if value.lower().strip() in film[field].lower())
