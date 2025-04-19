from functools import wraps

from src.exceptions import (
    SeriesNotFoundException,
    SeasonNotFoundException,
    EpisodeNotFoundException,
    EpisodeAlreadyExistsException,
    SeriesNotFoundHTTPException,
    SeasonNotFoundHTTPException,
    EpisodeNotFoundHTTPException,
    EpisodeAlreadyExistsHTTPException,
    EpisodeDoesNotExistException,
    EpisodeDoesNotExistHTTPException,
    UniqueEpisodePerSeasonException,
    UniqueEpisodePerSeasonHTTPException,
    UniqueSeasonPerSeriesException,
    UniqueSeasonPerSeriesHTTPException,
    UniqueFileIDHTTPException,
    UniqueFileIDException,
)


def handle_episode_exceptions(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except SeriesNotFoundException:
            raise SeriesNotFoundHTTPException
        except SeasonNotFoundException:
            raise SeasonNotFoundHTTPException
        except EpisodeNotFoundException:
            raise EpisodeNotFoundHTTPException
        except EpisodeAlreadyExistsException:
            raise EpisodeAlreadyExistsHTTPException
        except EpisodeDoesNotExistException:
            raise EpisodeDoesNotExistHTTPException
        except UniqueEpisodePerSeasonException:
            raise UniqueEpisodePerSeasonHTTPException
        except UniqueSeasonPerSeriesException:
            raise UniqueSeasonPerSeriesHTTPException
        except UniqueFileIDException:
            raise UniqueFileIDHTTPException

    return wrapper
