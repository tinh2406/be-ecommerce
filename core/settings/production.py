from os.path import join

from .base import *  # noqa: F403
from .base import BASE_DIR

# For security and performance reasons, DEBUG is turned off
DEBUG = False

STATIC_URL = "/static/"
STATICFILES_DIRS = [
    join(BASE_DIR, "static"),  # noqa: F405
]
