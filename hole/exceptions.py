"""Exceptions for *hole API Python client"""


class HoleError(Exception):
    """General HoleError exception occurred."""

    pass


class HoleConnectionError(HoleError):
    """When a connection error is encountered."""

    pass
