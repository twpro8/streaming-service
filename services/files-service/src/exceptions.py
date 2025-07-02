from fastapi.exceptions import HTTPException


class MasterException(Exception):
    detail = "Unexpected error"

    def __init__(self, detail: str = None, *args, **kwargs):
        self.detail = detail or self.detail
        super().__init__(self.detail, *args, **kwargs)

    def __str__(self):
        return self.detail


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


class InvalidContentTypeException(MasterException):
    detail = "Invalid content type"


class InvalidVideoTypeHTTPException(MasterHTTPException):
    status_code = 422
    detail = "Video must have mp4 or avi format"


class InvalidImageTypeHTTPException(MasterHTTPException):
    status_code = 422
    detail = "Image must have jpg or png format"


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


class NoTokenHTTPException(MasterHTTPException):
    status_code = 401
    detail = "No access token"


# Permissions
class PermissionDeniedHTTPException(MasterHTTPException):
    status_code = 403
    detail = "You do not have permission to access this resource"


# Images exceptions
class ImageNotFoundException(ObjectNotFoundException):
    detail = "Image not found"


class ImageNotFoundHTTPException(ObjectNotFoundHTTPException):
    detail = "Image does not exist"


# Videos exceptions
class VideoNotFoundException(ObjectNotFoundException):
    detail = "Video not found"


class VideoNotFoundHTTPException(ObjectNotFoundHTTPException):
    detail = "Video does not exist"
