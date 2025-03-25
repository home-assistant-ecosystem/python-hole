from .v5 import HoleV5
from .v6 import HoleV6
from .exceptions import HoleError


def Hole(*args, version=6, **kwargs):
    """Factory to get the correct Hole class for Pi-hole v5 or v6."""
    if version == 5:
        return HoleV5(*args, **kwargs)
    elif version == 6:
        return HoleV6(*args, **kwargs)
    else:
        raise HoleError(f"Unsupported Pi-hole version: {version}")
