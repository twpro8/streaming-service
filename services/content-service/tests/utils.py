import json


def pretty_print(obj):
    print(json.dumps(obj, indent=4, ensure_ascii=False))


def read_json(file_name: str) -> list[dict]:
    path = f"tests/mock_data/{file_name}.json"
    with open(path, encoding="utf-8") as file_in:
        return json.load(file_in)
