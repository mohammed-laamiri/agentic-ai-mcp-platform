"""
Custom exceptions for API client.
"""


class APIError(Exception):
    """Base exception for API errors."""
    pass


class APIConnectionError(APIError):
    """Raised when unable to connect to the backend API."""
    pass


class APINotFoundError(APIError):
    """Raised when a resource is not found (404)."""
    pass
