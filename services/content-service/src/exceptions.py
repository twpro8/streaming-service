from fastapi.exceptions import HTTPException


class MasterException(Exception):
    detail = "Unexpected error"

    def __init__(self, detail: str = None, *args, **kwargs):
        self.detail = detail or self.__class__.detail
        super().__init__(self.detail, *args, **kwargs)


class MasterHTTPException(HTTPException):
    status_code = 418
    detail = "I'm a teapot"

    def __init__(self, detail: str = None):
        self.detail = detail or self.__class__.detail
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


class MovieNotFoundException(ObjectNotFoundException):
    detail = "Movie not found"


class MovieNotFoundHTTPException(ObjectNotFoundHTTPException):
    detail = "Movie not found"


class ShowNotFoundException(ObjectNotFoundException):
    detail = "Show not found"


class MovieAlreadyExistsException(ObjectAlreadyExistsException):
    detail = "Movie already exists"


class MovieAlreadyExistsHTTPException(ObjectAlreadyExistsHTTPException):
    detail = "Movie with the provided data already exists"


class ShowNotFoundHTTPException(ObjectNotFoundHTTPException):
    detail = "Show not found"


class EpisodeNotFoundException(ObjectNotFoundException):
    detail = "Episode not found"


class ShowAlreadyExistsException(ObjectAlreadyExistsException):
    detail = "Show already exists"


class ShowAlreadyExistsHTTPException(ObjectAlreadyExistsHTTPException):
    detail = "Show already exists"


class ContentNotFoundException(ObjectNotFoundException):
    detail = "Content not found"


class ContentNotFoundHTTPException(ObjectNotFoundHTTPException):
    detail = "Movie or TV Show not found"


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


class UniqueSeasonPerShowException(UniqueViolationException):
    detail = "Unique season per show already exists"


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


class ActorAlreadyExistsException(ObjectAlreadyExistsException):
    detail = "Actor already exists"


class ActorAlreadyExistsHTTPException(ObjectAlreadyExistsHTTPException):
    detail = "Actor already exists"


class ActorNotFoundException(ObjectNotFoundException):
    detail = "Actor not found"


class ActorNotFoundHTTPException(ObjectNotFoundHTTPException):
    detail = "Actor not found"


class UnknownSortFieldHTTPException(MasterHTTPException):
    status_code = 422
    detail = "Unknown sort field"


class UnknownSortOrderHTTPException(MasterHTTPException):
    status_code = 422
    detail = "Unknown sort order. Use field:asc|desc"


class DirectorNotFoundException(ObjectNotFoundException):
    detail = "Director not found"


class DirectorNotFoundHTTPException(ObjectNotFoundHTTPException):
    detail = "Director not found"


class DirectorAlreadyExistsException(ObjectAlreadyExistsException):
    detail = "Director already exists"


class DirectorAlreadyExistsHTTPException(ObjectAlreadyExistsHTTPException):
    detail = "Director already exists"


class CountryNotFoundException(ObjectNotFoundException):
    detail = "Country not found"


class CountryNotFoundHTTPException(ObjectNotFoundHTTPException):
    detail = "Country not found"


class CountryAlreadyExistsException(ObjectAlreadyExistsException):
    detail = "Country already exists"


class CountryAlreadyExistsHTTPException(ObjectAlreadyExistsHTTPException):
    detail = "Country already exists"


class LanguageNotFoundException(ObjectNotFoundException):
    detail = "Language not found"


class LanguageNotFoundHTTPException(ObjectNotFoundHTTPException):
    detail = "Language not found"


class LanguageAlreadyExistsException(ObjectAlreadyExistsException):
    detail = "Language already exists"


class LanguageAlreadyExistsHTTPException(ObjectAlreadyExistsHTTPException):
    detail = "Language already exists"
