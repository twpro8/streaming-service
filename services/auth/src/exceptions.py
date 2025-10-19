"""
Custom exception classes for the application.

This module defines a hierarchy of custom exceptions to handle various error
scenarios in a structured way. It includes base exceptions for general errors,
HTTP-specific exceptions for web responses, and specialized exceptions for
different application services like JWT, Authentication, Redis, etc.
"""

from fastapi.exceptions import HTTPException
from typing import Dict, Any, Optional


class MasterException(Exception):
    """A base class for all custom exceptions in the application."""

    detail: str = "An unexpected internal error occurred."

    def __init__(self, detail: Optional[str] = None, *args: Any) -> None:
        """
        Initializes the exception, allowing for a dynamic detail message.

        Args:
            detail: An optional string to override the default detail message.
        """
        if detail is None:
            detail = self.detail
        super().__init__(detail, *args)


class MasterHTTPException(HTTPException):
    """A base class for all custom HTTP exceptions."""

    status_code: int = 500
    detail: str = "An unexpected server error occurred."

    def __init__(
        self,
        detail: Optional[str] = None,
        status_code: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Initializes the HTTP exception, allowing dynamic detail and status code.

        Args:
            detail: An optional string to override the default detail message.
            status_code: An optional integer to override the default status code.
            headers: Optional dictionary of headers to include in the response.
        """
        final_status_code = status_code if status_code is not None else self.status_code
        final_detail = detail if detail is not None else self.detail
        super().__init__(status_code=final_status_code, detail=final_detail, headers=headers)


# === Base Object Exceptions ===


class ObjectNotFoundException(MasterException):
    """Raised when a requested object is not found in the database."""

    detail = "Object not found."


class ObjectNotFoundHTTPException(MasterHTTPException):
    """HTTP exception for a 404 Not Found response."""

    status_code = 404
    detail = "Object not found."


class ObjectAlreadyExistsException(MasterException):
    """Raised when attempting to create an object that already exists."""

    detail = "Object already exists."


class ObjectAlreadyExistsHTTPException(MasterHTTPException):
    """HTTP exception for a 409 Conflict response."""

    status_code = 409
    detail = "Object already exists."


# === JWT Provider Exceptions ===


class JWTProviderException(MasterException):
    """Base exception for JWT provider errors."""


class InvalidCredentialsException(JWTProviderException):
    """Raised when a JWT token is invalid or cannot be verified."""

    detail = "Invalid JWT token."


class SignatureExpiredException(JWTProviderException):
    """Raised when a JWT token's signature has expired."""

    detail = "JWT token has expired."


# === User Exceptions ===


class UserException(MasterException):
    """Base exception for user-related errors."""


class UserHTTPException(MasterHTTPException):
    """Base HTTP exception for user-related errors."""


class UserNotFoundException(UserException, ObjectNotFoundException):
    """Raised when a specific user is not found."""

    detail = "User not found."


class UserNotFoundHTTPException(UserHTTPException, ObjectNotFoundHTTPException):
    """HTTP exception for when a user is not found (404)."""

    status_code = 404
    detail = "User not found."


# === Auth Exceptions ===


class BaseAuthException(MasterException):
    """Base exception for authentication and authorization errors."""


class BaseAuthHTTPException(MasterHTTPException):
    """Base HTTP exception for authentication errors, defaults to 401."""

    status_code = 401
    detail = "Authentication failed."


class IncorrectPasswordException(UserException):
    """Raised when the provided password is incorrect."""

    detail = "Incorrect password."


class IncorrectPasswordHTTPException(UserHTTPException):
    """HTTP exception for an incorrect password (401)."""

    status_code = 401
    detail = "Incorrect password."


class InvalidRefreshTokenException(BaseAuthException):
    """Raised when the provided refresh token is invalid or expired."""

    detail = "Invalid refresh token."


class InvalidRefreshTokenHTTPException(BaseAuthHTTPException):
    """HTTP exception for an invalid refresh token (403)."""

    status_code = 403
    detail = "Invalid refresh token."


class RefreshTokenNotFoundException(BaseAuthException, ObjectNotFoundException):
    """Raised when a refresh token is not found in storage."""

    detail = "Refresh token not found."


class NoRefreshTokenHTTPException(BaseAuthHTTPException):
    """HTTP exception for when a required refresh token is missing (403)."""

    status_code = 403
    detail = "No refresh token provided."


class NoAccessTokenHTTPException(MasterHTTPException):
    """HTTP exception for when a required access token is missing (403)."""

    status_code = 403
    detail = "No access token provided."


class InvalidAccessTokenHTTPException(MasterHTTPException):
    """HTTP exception for an invalid or expired access token (403)."""

    status_code = 403
    detail = "Invalid access token."


# === Password Hasher Exceptions ===


class BaseHasherException(MasterException):
    """Base exception for password hashing errors."""


class InvalidHashValueException(BaseHasherException):
    """Raised when the hash value is invalid or malformed."""

    detail = "Invalid hash value."


# === Redis Manager Exceptions ===


class RedisManagerException(MasterException):
    """Base exception for RedisManager errors."""

    detail = "Redis manager error."


class RedisConnectionException(RedisManagerException):
    """Raised on failure to connect to the Redis server."""

    detail = "Failed to connect to Redis."


class RedisAuthenticationException(RedisManagerException):
    """Raised on failure to authenticate with the Redis server."""

    detail = "Failed to authenticate with Redis."


class RedisOperationException(RedisManagerException):
    """Raised when a Redis operation (e.g., SET, GET) fails."""

    detail = "Redis operation failed."


# === Aiohttp Client Exceptions ===


class AiohttpClientException(MasterException):
    """Base exception for the custom aiohttp client wrapper."""

    detail = "HTTP client error."


class AiohttpConnectionException(AiohttpClientException):
    """Raised when the client cannot connect to the remote server."""

    detail = "Error connecting to the remote server."


class AiohttpTimeoutException(AiohttpClientException):
    """Raised when a request to the remote server times out."""

    detail = "Request timed out."


class AiohttpResponseException(AiohttpClientException):
    """Raised on non-2xx responses or errors processing the response."""

    detail = "Invalid response from the remote server."


class AiohttpNotInitializedException(AiohttpClientException):
    """Raised when trying to use the client before it has been initialized."""

    detail = "Aiohttp client has not been initialized."


# === Google OAuth Client Exceptions ===


class GoogleOAuthClientException(MasterException):
    """Base exception for the Google OAuth client."""

    detail = "Google OAuth client error."


class NoIDTokenException(GoogleOAuthClientException):
    """Raised when the token response does not include an 'id_token'."""

    detail = "No ID token found in the response."


class InvalidStateException(GoogleOAuthClientException):
    """Raised when the OAuth 'state' parameter is invalid or expired."""

    detail = "State is invalid or expired."


class InvalidStateHTTPException(MasterHTTPException):
    """HTTP exception for an invalid OAuth 'state' (422)."""

    status_code = 422
    detail = "State is invalid or expired."


class JWKSFetchException(GoogleOAuthClientException):
    """Raised when the Google JWKS (JSON Web Key Set) cannot be fetched."""

    detail = "Could not fetch JWKS from Google."


class TokenVerificationException(GoogleOAuthClientException):
    """Raised when a Google ID token fails verification."""

    detail = "Google ID token verification failed."
