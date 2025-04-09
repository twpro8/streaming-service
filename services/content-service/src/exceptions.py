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


# Films
class FilmNotFoundException(ObjectNotFoundException):
    detail = "Film not found"


class FilmNotFoundHTTPException(ObjectNotFoundHTTPException):
    status_code = 404
    detail = "Film not found"


class SeriesNotFoundException(ObjectNotFoundException):
    detail = "Film not found"


class SeriesNotFoundHTTPException(ObjectNotFoundHTTPException):
    status_code = 404
    detail = "Film not found"
