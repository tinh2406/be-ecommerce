from .base import *  # noqa: F403

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True


# Đọc biến môi trường
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",  # Sử dụng SQLite cho tests
        "NAME": (BASE_DIR, "test_db.sqlite3"),  # noqa: F405  # Đặt tên cho DB tạm
    }
}
