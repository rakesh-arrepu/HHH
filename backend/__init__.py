# Mark minimal.backend as a package to enable explicit relative imports and avoid name collisions
# with the main backend package (backend/src/models, etc.).

# Expose common submodules if needed by external imports
from . import models as models  # noqa: F401
from . import database as database  # noqa: F401
from . import auth as auth  # noqa: F401

__all__ = ["models", "database", "auth"]
