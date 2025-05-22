from enum import Enum


class Quality(str, Enum):
    CD = "360p"
    SD = "480p"
    HD = "720p"
    FHD = "1080p"

    def __str__(self):
        return self.value
