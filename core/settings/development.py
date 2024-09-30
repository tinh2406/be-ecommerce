from os.path import join

from .base import *  # noqa: F403
from .base import BASE_DIR

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

STATIC_URL = "/static/"
STATICFILES_DIRS = [
    join(BASE_DIR, "static"),
]
