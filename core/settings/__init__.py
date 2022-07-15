import os

from .base import *  # noqa: F403, F401

if os.getenv("ENV_NAME") == "Production":
    from .production import *  # noqa: F403, F401
elif os.getenv("ENV_NAME") == "Staging":
    from .staging import *  # noqa: F403, F401
else:
    from .local import *  # noqa: F403, F401
