"""
Custom exception classes for the application.

This module defines a hierarchy of custom exceptions to handle various error
scenarios in a structured way. It includes base exceptions for general errors
and specialized exceptions for different application services.
"""


class MasterException(Exception):
    status_code: int = 500
    detail: str = "Unexpected error"

    def __init__(self, detail: str = None, *args):
        if detail:
            self.detail = detail
        super().__init__(self.detail, *args)


# ---------- Base exceptions ----------


class UnauthorizedException(MasterException):
    status_code = 401
    detail = "Unauthorized"


class ForbiddenException(MasterException):
    status_code = 403
    detail = "Forbidden"


class NotFoundException(MasterException):
    status_code = 404
    detail = "Not Found"


class AlreadyExistsException(MasterException):
    status_code = 409
    detail = "Already Exists"


class ValidationException(MasterException):
    status_code = 422
    detail = "Validation Error"


# ---------- Auth exceptions ----------


class SignatureExpiredException(UnauthorizedException):
    detail = "Signature has expired"


class InvalidTokenException(UnauthorizedException):
    detail = "Token is invalid or expired"


class NoAccessTokenException(UnauthorizedException):
    detail = "No access token"


class PermissionDeniedException(ForbiddenException):
    detail = "You do not have permission to access this resource"


# --------- Movie exceptions ----------


class MovieNotFoundException(NotFoundException):
    detail = "Movie not found"


class MovieAlreadyExistsException(AlreadyExistsException):
    detail = "Movie already exists. Combination title and release date must be unique."


# ---------- Show exceptions ----------


class ShowNotFoundException(NotFoundException):
    detail = "Show not found"


class ShowAlreadyExistsException(AlreadyExistsException):
    detail = "Show already exists. Combination title and release date must be unique."


# -------- Season exceptions ----------


class SeasonNotFoundException(NotFoundException):
    detail = "Season not found"


class SeasonAlreadyExistsException(AlreadyExistsException):
    detail = "Unique season per show already exists"


# -------- Episode exceptions ----------


class EpisodeNotFoundException(NotFoundException):
    detail = "Episode not found"


class EpisodeAlreadyExistsException(AlreadyExistsException):
    detail = "Unique episode per season already exists"


# -------- Director exceptions ---------


class DirectorNotFoundException(NotFoundException):
    detail = "Director not found"


class DirectorAlreadyExistsException(AlreadyExistsException):
    detail = "Director already exists"


# --------- Actor exceptions -----------


class ActorNotFoundException(NotFoundException):
    detail = "Actor not found"


class ActorAlreadyExistsException(AlreadyExistsException):
    detail = "Actor already exists"


# -------- Comment exceptions ----------


class CommentNotFoundException(NotFoundException):
    detail = "Comment not found"


# --------- Genre exceptions -----------


class GenreNotFoundException(NotFoundException):
    detail = "Genre not found"


class GenreAlreadyExistsException(AlreadyExistsException):
    detail = "Genre already exists"


# -------- Country exceptions ----------


class CountryNotFoundException(NotFoundException):
    detail = "Country not found"


class CountryAlreadyExistsException(AlreadyExistsException):
    detail = "Country already exists"


# -------- Language exceptions ---------


class LanguageNotFoundException(NotFoundException):
    detail = "Language not found"


class LanguageAlreadyExistsException(AlreadyExistsException):
    detail = "Language already exists"


# -------- Cover URL exceptions --------


class VideoUrlAlreadyExistsException(AlreadyExistsException):
    detail = "Video URL already exists"


# -------- Video URL exceptions --------


class CoverUrlAlreadyExistsException(AlreadyExistsException):
    detail = "Cover URL already exists"


# -------- Content exceptions ----------


class ContentNotFoundException(NotFoundException):
    detail = "Content not found"


# -------- Validation exceptions -------


class FieldRequiredException(ValidationException):
    detail = "At least one field must be provided"


class UnknownSortFieldException(ValidationException):
    detail = "Unknown sort field"


class UnknownSortOrderException(ValidationException):
    detail = "Unknown sort order. Use field:asc|desc"
