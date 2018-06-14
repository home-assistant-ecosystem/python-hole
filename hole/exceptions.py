"""
Copyright (c) 2018 Fabian Affolter <fabian@affolter-engineering.ch>

Licensed under MIT. All rights reserved.
"""


class HoleError(Exception):
    """General HoleError exception occurred."""

    pass


class HoleConnectionError(HoleError):
    """When a connection error is encountered."""

    pass
