from pydantic import AnyUrl


def normalize_for_insert(data: dict) -> dict:
    def normalize(value):
        if isinstance(value, AnyUrl):
            return str(value)
        return value

    return {key: normalize(val) for key, val in data.items()}
