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
class UsersException(MasterHTTPException): ...


class UserNotFoundException(UsersException, ObjectNotFoundException):
    detail = "User not found"


class IncorrectPasswordException(UsersException):
    detail = "Incorrect password"


class InvalidUsersDataException(UsersException):
    detail = "Incorrect user data"


class UsersHTTPException(MasterHTTPException): ...


class UserNotFoundHTTPException(UsersException, ObjectNotFoundHTTPException):
    status_code = 404
    detail = "User not found"


class IncorrectPasswordHTTPException(UsersHTTPException):
    status_code = 401
    detail = "Incorrect password"


class InvalidFriendIdException(UsersHTTPException):
    status_code = 422
    detail = "Friend ID cannot be equal to users one"


# Friendships
class FriendshipAlreadyExistsException(ObjectAlreadyExistsException):
    detail = "Friendship already exists"


class FriendshipAlreadyExistsHTTPException(ObjectAlreadyExistsHTTPException):
    status_code = 409
    detail = "Friendship already exists"


# Films and Series exceptions
class FilmNotFoundException(ObjectNotFoundException):
    detail = "Film not found"


class FilmNotFoundHTTPException(ObjectNotFoundHTTPException):
    status_code = 404
    detail = "Film not found"


class AlreadyInFavoritesException(ObjectAlreadyExistsException):
    detail = "Film or TV Series is already in favorites"


class AlreadyInFavoritesHTTPException(ObjectAlreadyExistsHTTPException):
    status_code = 409
    detail = "Film or TV Series is already in favorites"
