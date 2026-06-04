"""Exceptions for *hole API Python client"""


class HoleError(Exception):
    """General HoleError exception occurred."""

    def __init__(self, message: str, *, status: int | None = None) -> None:
        """Initialize the error, optionally carrying the HTTP status code."""
        super().__init__(message)
        self.status = status


class HoleConnectionError(HoleError):
    """When a connection error is encountered."""


class HoleAuthenticationError(HoleError):
    """When authentication is required, missing, or invalid (HTTP 401)."""


class HoleResponseError(HoleError):
    """When the API returns an unexpected or unparseable payload."""
