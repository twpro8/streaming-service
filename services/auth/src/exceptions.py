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


class JWTTokenHTTPException(MasterHTTPException): ...


class SignatureExpiredHTTPException(JWTTokenHTTPException):
    status_code = 401
    detail = "Signature has expired: JWT"


class InvalidCredentialsHTTPException(JWTTokenHTTPException):
    status_code = 401
    detail = "Could not validate credentials: JWT"


# === JWT Provider Exceptions ===
class JWTProviderException(MasterException):
    """Base exception for JWT provider."""


class InvalidCredentialsException(JWTProviderException):
    """Raised when the token is invalid or cannot be verified."""
    detail = "Invalid JWT token."


class SignatureExpiredException(JWTProviderException):
    """Raised when the token has expired."""
    detail = "JWT token has expired."


# === User Exceptions ===
class UserException(MasterException): ...


class UserHTTPException(MasterHTTPException): ...


class UserNotFoundException(UserException, ObjectNotFoundException):
    detail = "User not found"


class InvalidUserDataException(UserException):
    detail = "Incorrect user data"


class UserNotFoundHTTPException(UserHTTPException, ObjectNotFoundHTTPException):
    status_code = 404
    detail = "User not found"


class IncorrectPasswordException(UserException):
    detail = "Incorrect password"


class IncorrectPasswordHTTPException(UserHTTPException):
    status_code = 401
    detail = "Incorrect password"


class InvalidRefreshTokenException(MasterException):
    detail = "Invalid refresh token"


class InvalidRefreshTokenHTTPException(MasterHTTPException):
    status_code = 403
    detail = "Invalid refresh token"


class RefreshTokenNotFoundException(ObjectNotFoundException):
    detail = "Refresh token not found"


class RefreshTokenNotFoundHTTPException(MasterHTTPException):
    status_code = 403
    detail = "Refresh token not found"


class InvalidHashValueException(MasterException):
    detail = "Invalid hash value"


# === Redis Manager Exceptions ===
class RedisManagerException(MasterException):
    """Base exception for RedisManager."""
    detail = "Redis manager error"


class RedisConnectionException(RedisManagerException):
    """Redis connection error."""
    detail = "Failed to connect to Redis"


class RedisAuthenticationException(RedisManagerException):
    """Redis authentication error."""
    detail = "Failed to authenticate with Redis"


class RedisOperationException(RedisManagerException):
    """Redis operation error."""
    detail = "Redis operation error"


# === Aiohttp Client Exceptions ===
class AiohttpClientException(MasterException):
    """Base exception for the HTTP client."""
    detail = "HTTP client error"


class AiohttpConnectionException(AiohttpClientException):
    """Error connecting to the remote server."""
    detail = "Error connecting to the remote server"


class AiohttpTimeoutException(AiohttpClientException):
    """Timeout error during request."""
    detail = "Request timed out"


class AiohttpResponseException(AiohttpClientException):
    """Error processing the response from the server."""
    detail = "Aiohttp response error"


class AiohttpNotInitializedException(AiohttpClientException):
    """Error accessing an uninitialized client."""
    detail = "Aiohttp client not initialized."


# === Google OAuth Client Exceptions ===
class GoogleOAuthClientException(MasterException):
    """Base exception for Google OAuth client."""
    detail = "Google OAuth client error"


class NoIDTokenException(GoogleOAuthClientException):
    """Raised when the token response does not include an ID token."""
    detail = "No ID token found in the response"


class InvalidStateException(GoogleOAuthClientException):
    """Raised when the OAuth state parameter is invalid or expired."""
    detail = "State is invalid or expired"


class InvalidStateHTTPException(MasterHTTPException):
    status_code = 422
    detail = "State is invalid or expired"


class JWKSFetchException(GoogleOAuthClientException):
    """Raised when JWKS could not be fetched or parsed."""
    detail = "JWKS could not be fetched"


class TokenVerificationException(GoogleOAuthClientException):
    """Raised when Google ID token verification fails."""
    detail = "Token verification failed"
