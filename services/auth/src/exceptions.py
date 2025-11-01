"""
Custom exception classes for the application.

This module defines a hierarchy of custom exceptions to handle various error
scenarios in a structured way. It includes base exceptions for general errors
and specialized exceptions for different application services.
"""


class MasterException(Exception):
    status_code: int = 500
    detail: str = "Unexpected error"

    def __init__(self, status_code: int = None, detail: str = None, *args):
        if status_code:
            self.status_code = status_code
        if detail:
            self.detail = detail
        super().__init__(self.detail, *args)


# ---------- Base exceptions ----------


class BadRequest(MasterException):
    status_code = 400
    detail = "Bad Request"


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


class TooManyRequestsException(MasterException):
    status_code = 429
    detail = "Too many requests"


# ---------- Auth exceptions ----------


class SignatureExpiredException(UnauthorizedException):
    detail = "Signature has expired"


class InvalidTokenException(UnauthorizedException):
    detail = "Token is invalid or expired"


class NoAccessTokenException(UnauthorizedException):
    detail = "No access token"


class NoRefreshTokenException(UnauthorizedException):
    detail = "No refresh token"


class PermissionDeniedException(ForbiddenException):
    detail = "You do not have permission to access this resource"


class AlreadyAuthorizedException(AlreadyExistsException):
    detail = "User is already authorized on this device"


class IncorrectPasswordException(UnauthorizedException):
    detail = "Incorrect password"


class InvalidRefreshTokenException(UnauthorizedException):
    detail = "Invalid refresh token"


class RefreshTokenAlreadyExists(AlreadyExistsException):
    detail = "Refresh token already exists"


class TokenRevokedException(UnauthorizedException):
    detail = "Token has been revoked"


class ClientMismatchException(UnauthorizedException):
    detail = "Client mismatch"


class InvalidVerificationCodeException(BadRequest):
    detail = "Invalid or expired code"


class UserUnverifiedException(UnauthorizedException):
    detail = "User unverified. Please verify your email first"


class UserAlreadyVerifiedException(AlreadyExistsException):
    detail = "User is already verified"


class SamePasswordException(BadRequest):
    detail = "New password must be different"


# ------ JWT Provider Exceptions -------


class JWTProviderException(MasterException):
    """Base exception for JWT provider errors."""


# ---------- User exceptions ----------


class UserNotFoundException(NotFoundException):
    detail = "User not found"


class UserAlreadyExistsException(AlreadyExistsException):
    detail = "User with the provided email already exists"


# ---- Password Hasher exceptions ----


class BaseHasherException(MasterException):
    """Base exception for password hashing errors."""


class InvalidHashValueException(BaseHasherException):
    """Raised when the hash value is invalid or malformed."""

    detail = "Invalid hash value"


# ---- Redis Manager Exceptions ----


class RedisManagerException(MasterException):
    detail = "Redis manager error"


class RedisConnectionException(RedisManagerException):
    detail = "Failed to connect to Redis"


class RedisAuthenticationException(RedisManagerException):
    detail = "Failed to authenticate with Redis"


class RedisOperationException(RedisManagerException):
    detail = "Redis operation failed"


# ---- Aiohttp Client exceptions ----


class AiohttpClientException(MasterException):
    detail = "HTTP client error"


class AiohttpConnectionException(AiohttpClientException):
    detail = "Error connecting to the remote server"


class AiohttpTimeoutException(AiohttpClientException):
    detail = "Request timed out"


class AiohttpResponseException(AiohttpClientException):
    detail = "Invalid response from the remote server"


class AiohttpNotInitializedException(AiohttpClientException):
    detail = "Aiohttp client has not been initialized"


# --- Google OAuth Client Exceptions ---


class GoogleOAuthClientException(MasterException):
    detail = "Google OAuth client error"


class NoIDTokenException(GoogleOAuthClientException):
    detail = "No ID token found in the response"


class InvalidStateException(ValidationException):
    detail = "State is invalid or expired"


class JWKSFetchException(GoogleOAuthClientException):
    detail = "Could not fetch JWKS from Google"


class TokenVerificationException(GoogleOAuthClientException):
    detail = "Google ID token verification failed"


# -------- Validation exceptions -------


class FieldRequiredException(ValidationException):
    detail = "At least one field must be provided"
