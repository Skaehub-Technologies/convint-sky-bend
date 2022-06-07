import os

from .base import *  # noqa

if os.getenv("ENV_NAME") == "Production":
    from .production import *  # noqa
elif os.getenv("ENV_NAME") == "Staging":
    from .staging import *  # noqa
else:
    from .local import *  # noqa
