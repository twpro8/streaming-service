from fastapi.exceptions import HTTPException


class MasterException(Exception):
    detail = "Unexpected error"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)


class MasterHTTPException(HTTPException):
    status_code = 418
    detail = "I'm a teapot"

    def __init__(self):
        super().__init__(status_code=self.status_code, detail=self.detail)


# Base Exceptions
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


# JWT Exceptions
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


# Permissions
class PermissionDeniedHTTPException(MasterHTTPException):
    status_code = 403
    detail = "You do not have permission to access this resource"


# Content
class FilmNotFoundException(ObjectNotFoundException):
    detail = "Film not found"


class FilmNotFoundHTTPException(ObjectNotFoundHTTPException):
    status_code = 404
    detail = "Film not found"


class SeriesNotFoundException(ObjectNotFoundException):
    detail = "Series not found"


class SeriesNotFoundHTTPException(ObjectNotFoundHTTPException):
    status_code = 404
    detail = "Series not found"


class EpisodeNotFoundException(ObjectNotFoundException):
    detail = "Episode not found"


class EpisodeNotFoundHTTPException(ObjectNotFoundHTTPException):
    status_code = 404
    detail = "Episode not found"


class SeasonNotFoundException(ObjectNotFoundException):
    detail = "Season not found"


class SeasonNotFoundHTTPException(ObjectNotFoundHTTPException):
    status_code = 404
    detail = "Season not found"


class EpisodeDoesNotExistHTTPException(ObjectNotFoundHTTPException):
    status_code = 204
    detail = "Episode does not exist"


class EpisodeDoesNotExistException(ObjectNotFoundException):
    detail = "Episode does not exist"


class EpisodeAlreadyExistsException(ObjectAlreadyExistsException):
    detail = "Episode already exists"


class EpisodeAlreadyExistsHTTPException(ObjectAlreadyExistsHTTPException):
    status_code = 409
    detail = "Episode with the provided data already exists."


class UniqueViolationException(MasterException):
    detail = "Unique violation error"


class UniqueViolationHTTPException(MasterHTTPException):
    status_code = 409
    detail = "Unique violation error"


class UniqueEpisodePerSeasonException(UniqueViolationException):
    detail = "Unique episode per season already exists"


class UniqueSeasonPerSeriesException(UniqueViolationException):
    detail = "Unique episode per season already exists"


class UniqueFileIDException(UniqueViolationException):
    detail = "Unique file id already exists"


class UniqueEpisodePerSeasonHTTPException(UniqueViolationHTTPException):
    status_code = 409
    detail = "Unique episode per season already exists"


class UniqueSeasonPerSeriesHTTPException(UniqueViolationHTTPException):
    status_code = 409
    detail = "Unique episode per season already exists"


class UniqueFileIDHTTPException(UniqueViolationHTTPException):
    status_code = 409
    detail = "Unique file id already exists"
