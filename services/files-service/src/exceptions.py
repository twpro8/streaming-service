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
    status_code = 404
    detail = "Object not found"
