from enum import Enum


class VideoType(str, Enum):
    film = "film"
    episode = "episode"

    def __str__(self):
        return self.value


class ContentType(str, Enum):
    film = "film"
    episode = "episode"
    image = "image"

    def __str__(self):
        return self.value


class Qualities(str, Enum):
    CD = "360p"
    SD = "480p"
    HD = "720p"
    FHD = "1080p"

    def __str__(self):
        return self.value
