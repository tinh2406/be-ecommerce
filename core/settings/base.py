from os.path import join

from . import BASE_DIR, env

# SECURITY WARNING: keep the secret key used in production secret!
# Raises ImproperlyConfigured exception if SECRET_KEY not in os.environ
SECRET_KEY = env("SECRET_KEY")
API_HOST = env("API_HOST")
API_PORT = env("API_PORT")

# Redis
REDIS_HOST = env("REDIS_HOST", default="localhost")
REDIS_PORT = env("REDIS_PORT", default=6379)
REDIS_PASSWORD = env("REDIS_PASSWORD", default="yourpassword")
REDIS_URL = f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/"
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
        "KEY_PREFIX": "imdb",
        "TIMEOUT": 60 * 15,  # in seconds: 60 * 15 (15 minutes)
    }
}

RABBITMQ_AMQP_HOST = env("RABBITMQ_AMQP_HOST", default="localhost")
RABBITMQ_AMQP_PORT = env("RABBITMQ_AMQP_PORT", default=5672)
RABBITMQ_DEFAULT_USER = env("RABBITMQ_DEFAULT_USER", default="guest")
RABBITMQ_DEFAULT_PASS = env("RABBITMQ_DEFAULT_PASS", default="guest")

# Celery
CELERY_BROKER_URL = f"amqp://{RABBITMQ_DEFAULT_USER}:{RABBITMQ_DEFAULT_PASS}@{RABBITMQ_AMQP_HOST}:{RABBITMQ_AMQP_PORT}//"

# Định dạng và giao thức serialization
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"

CELERY_TIMEZONE = None  # Không sử dụng múi giờ
CELERY_ENABLE_UTC = False  # Không sử dụng UTC

# Lưu kết quả vào RabbitMQ (sử dụng RPC):
CELERY_RESULT_BACKEND = "rpc://"

# Tự động kết nối lại nếu kết nối với broker bị mất khi khởi động
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# ElasticSearch
ELASTICSEARCH_HOST = env("ELASTICSEARCH_HOST", default="localhost")
ELASTICSEARCH_PORT = env("ELASTICSEARCH_PORT", default=9200)
ELASTIC_USERNAME = env("ELASTIC_USERNAME", default="elastic")
ELASTIC_PASSWORD = env("ELASTIC_PASSWORD", default="changeme")
ELASTICSEARCH_URL = f"http://{ELASTIC_USERNAME}:{ELASTIC_PASSWORD}@{ELASTICSEARCH_HOST}:{ELASTICSEARCH_PORT}/"
ELASTICSEARCH_DSL = {
    "default": {
        "hosts": [ELASTICSEARCH_URL],
    },
}

# # EMAIL related settings
EMAIL_BACKEND = env(
    "EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_HOST = env("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = env("EMAIL_PORT", default=587)
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")

# Application definition
DJANGO_APPS = (
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
)
THIRD_PARTY_APPS = (
    "rest_framework",
    "django_elasticsearch_dsl",
    "corsheaders",
    'django_celery_beat',
    "django_crontab",
    "django_filters",
    "bandit",
    "django_nose",
    "djongo"
)
LOCAL_APPS = ("users", "products", "crawlers")
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

AUTH_USER_MODEL = "users.User"

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Config django-cors lib
CORS_ORIGIN_ALLOW_ALL = env.bool("CORS_ORIGIN_ALLOW_ALL", default=False)
CORS_ORIGIN_WHITELIST = env.list(
    "CORS_ORIGIN_WHITELIST",
    default=[
        "http://127.0.0.1:8001",
        "http://localhost:8001",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
)
CORS_ORIGIN_REGEX_WHITELIST = env.list("CORS_ORIGIN_WHITELIST", default=[])
CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

# Config Django Rest framework
REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "users.services.authentication.JWTAuthentication",
    ],
    "DEFAULT_PAGINATION_CLASS": "core.utils.BasePagination",
    "PAGE_SIZE": 12,
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
}

# Testing
# Use nose to run all tests
TEST_RUNNER = "django_nose.NoseTestSuiteRunner"

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            join(BASE_DIR, "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"


# Database


def db_config(prefix="", test=None):
    if test is None:
        test = {}
    return {
        "ENGINE": "django.db.backends.mysql",
        "NAME": env("MYSQL_DATABASE"),
        "USER": "root",
        "PASSWORD": env("MYSQL_ROOT_PASSWORD"),
        "HOST": env("MYSQL_HOST"),
        "PORT": env("MYSQL_PORT"),
        "OPTIONS": {
            "init_command": "SET GLOBAL max_connections = 100000",
            "charset": "utf8mb4",
        },
    }


def mongo_config(prefix="", test=None):
    if test is None:
        test = {}
    return {
        'ENGINE': 'djongo',
        'NAME': env('MONGO_DATABASE'),
        'CLIENT': {
            'host': env('MONGO_HOST'),
        }
    }


DATABASES = {
    "default": db_config(),
    "mongo": mongo_config(),
}

DATABASE_ROUTERS = ['core.db_routers.DBRouter']

# Password validation
# https://docs.djangoproject.com/en/2.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.2/topics/i18n/
LANGUAGE_CODE = env("LANGUAGE_CODE", default="en-us")
TIME_ZONE = "Asia/Ho_Chi_Minh"

USE_I18N = True

USE_L10N = True
USE_TZ = True

# https://docs.djangoproject.com/en/2.2/howto/static-files/
STATIC_URL = "/static/"
