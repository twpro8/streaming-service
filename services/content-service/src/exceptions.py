from fastapi.exceptions import HTTPException


class MasterException(Exception):
    detail = "Unexpected error"

    def __init__(self, detail: str = None, *args, **kwargs):
        self.detail = detail or self.__class__.detail
        super().__init__(self.detail, *args, **kwargs)


class MasterHTTPException(HTTPException):
    status_code = 418
    detail = "I'm a teapot"

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


class ObjectNotFoundException(MasterException):
    detail = "Object not found"


class ObjectNotFoundHTTPException(MasterHTTPException):
    status_code = 404
    detail = "Object not found"


class ObjectAlreadyExistsException(MasterException):
    detail = "Object already exists"


class ObjectAlreadyExistsHTTPException(MasterHTTPException):
    status_code = 409
    detail = "Object already exists"


class ForeignKeyViolationException(MasterException):
    detail = "Foreign key violation"


class JWTTokenException(MasterException): ...


class SignatureExpiredException(JWTTokenException):
    detail = "Signature has expired: JWT"


class InvalidCredentialsException(JWTTokenException):
    detail = "Could not validate credentials: JWT"


class JWTTokenHTTPException(MasterHTTPException): ...


class SignatureExpiredHTTPException(JWTTokenHTTPException):
    status_code = 401
    detail = "Signature has expired: JWT"


class InvalidCredentialsHTTPException(JWTTokenHTTPException):
    status_code = 401
    detail = "Could not validate credentials: JWT"


class NoTokenHTTPException(JWTTokenHTTPException):
    status_code = 401
    detail = "No token"


class PermissionDeniedHTTPException(MasterHTTPException):
    status_code = 403
    detail = "You do not have permission to access this resource"


class FilmNotFoundException(ObjectNotFoundException):
    detail = "Film not found"


class FilmNotFoundHTTPException(ObjectNotFoundHTTPException):
    detail = "Film not found"


class SeriesNotFoundException(ObjectNotFoundException):
    detail = "Series not found"


class FilmAlreadyExistsException(ObjectAlreadyExistsException):
    detail = "Film already exists"


class FilmAlreadyExistsHTTPException(ObjectAlreadyExistsHTTPException):
    detail = "Film with the provided data already exists"


class SeriesNotFoundHTTPException(ObjectNotFoundHTTPException):
    detail = "Series not found"


class EpisodeNotFoundException(ObjectNotFoundException):
    detail = "Episode not found"


class ContentNotFoundException(ObjectNotFoundException):
    detail = "Content not found"


class ContentNotFoundHTTPException(ObjectNotFoundHTTPException):
    detail = "Film or TV Series not found"


class EpisodeNotFoundHTTPException(ObjectNotFoundHTTPException):
    detail = "Episode not found"


class SeasonNotFoundException(ObjectNotFoundException):
    detail = "Season not found"


class SeasonNotFoundHTTPException(ObjectNotFoundHTTPException):
    detail = "Season not found"


class EpisodeDoesNotExistException(ObjectNotFoundException):
    detail = "Episode does not exist"


class EpisodeAlreadyExistsException(ObjectAlreadyExistsException):
    detail = "Episode already exists"


class EpisodeAlreadyExistsHTTPException(ObjectAlreadyExistsHTTPException):
    detail = "Episode with the provided data already exists."


class UniqueViolationException(MasterException):
    detail = "Unique violation error"


class UniqueViolationHTTPException(MasterHTTPException):
    status_code = 409
    detail = "Unique violation error"


class AtLeastOneFieldRequiredException(MasterHTTPException):
    status_code = 422
    detail = "At least one field must be provided"


class UniqueCoverURLException(UniqueViolationException):
    detail = "Cover URL unique violation error"


class UniqueVideoURLException(UniqueViolationException):
    detail = "Cover URL unique violation error"


class UniqueCoverURLHTTPException(UniqueViolationHTTPException):
    detail = "Cover URL has to be unique"


class UniqueVideoURLHTTPException(UniqueViolationHTTPException):
    detail = "Video URL is already in use"


class UniqueEpisodePerSeasonException(UniqueViolationException):
    detail = "Unique episode per season already exists"


class UniqueSeasonPerSeriesException(UniqueViolationException):
    detail = "Unique episode per season already exists"


class UniqueFileURLException(UniqueViolationException):
    detail = "Unique file URL already exists"


class UniqueEpisodePerSeasonHTTPException(UniqueViolationHTTPException):
    detail = "Episode number already exists"


class UniqueFileURLHTTPException(UniqueViolationHTTPException):
    detail = "Unique file URL already exists"


class SeasonAlreadyExistsException(ObjectAlreadyExistsException):
    detail = "Season already exists"


class SeasonAlreadyExistsHTTPException(ObjectAlreadyExistsHTTPException):
    detail = "Season with the provided number already exists"


class CommentNotFoundException(ObjectNotFoundException):
    detail = "Comment not found"


class CommentNotFoundHTTPException(ObjectNotFoundHTTPException):
    detail = "Comment not found"


class GenreNotFoundException(ObjectNotFoundException):
    detail = "Genre not found"


class GenreNotFoundHTTPException(ObjectNotFoundHTTPException):
    detail = "Genre not found"


class GenreAlreadyExistsException(ObjectAlreadyExistsException):
    detail = "Genre already exists"


class GenreAlreadyExistsHTTPException(ObjectAlreadyExistsHTTPException):
    detail = "Genre already exists"
