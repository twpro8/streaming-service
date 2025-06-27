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


class InvalidContentTypeException(MasterException):
    detail = "Invalid content type"


class InvalidVideoTypeHTTPException(MasterHTTPException):
    status_code = 422
    detail = "Video must have mp4 or avi format"


class InvalidImageTypeHTTPException(MasterHTTPException):
    status_code = 422
    detail = "Image must have jpg or png format"
