from enum import Enum


class ContentType(str, Enum):
    films = "films"
    series = "series"
    covers = "covers"

    def __str__(self):
        return self.value
