import os

from .base import *

if os.getenv("ENV_NAME") == "Production":
    from .production import *
elif os.getenv("ENV_NAME") == "Staging":
    from .staging import *
else:
    from .local import *
