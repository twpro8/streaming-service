from fastapi.exceptions import HTTPException


class MasterException(Exception):
    detail = "Unexpected error"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)


class MasterHTTPException(HTTPException):
    status_code = 500
    detail = "Unexpected error"

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


# Users Exceptions
class UsersException(MasterException): ...


class UsersHTTPException(MasterHTTPException): ...


class UserNotFoundException(UsersException, ObjectNotFoundException):
    detail = "User not found"


class InvalidUsersDataException(UsersException):
    detail = "Incorrect user data"


class UserNotFoundHTTPException(UsersHTTPException, ObjectNotFoundHTTPException):
    status_code = 404
    detail = "User not found"


class IncorrectPasswordException(UsersException):
    detail = "Incorrect password"


class IncorrectPasswordHTTPException(UsersHTTPException):
    status_code = 401
    detail = "Incorrect password"


class InvalidStateException(MasterException):
    detail = "State is invalid or expired"


class InvalidStateHTTPException(MasterHTTPException):
    status_code = 422
    detail = "State is invalid or expired"


class NoIDTokenException(MasterException):
    detail = "No ID token found in the response"


class NoIDTokenHTTPException(MasterHTTPException):
    detail = "No ID token found in the response"
