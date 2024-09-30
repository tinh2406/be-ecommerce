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
REDIS_URL = f"redis://{REDIS_HOST}:{REDIS_PORT}/"
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
        "KEY_PREFIX": "imdb",
        "TIMEOUT": 60 * 15,  # in seconds: 60 * 15 (15 minutes)
    }
}

# Celery
CELERY_BROKER_URL = (
    "redis://localhost:6379/0"  # Hoặc 'amqp://localhost' nếu sử dụng RabbitMQ
)
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
CELERY_RESULT_SERIALIZER = "json"

CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# ActiveMQ
ACTIVEMQ_ADMIN_LOGIN = env("ACTIVEMQ_ADMIN_LOGIN")
ACTIVEMQ_ADMIN_PASSWORD = env("ACTIVEMQ_ADMIN_PASSWORD")
ACTIVEMQ_WEB_CONSOLE_PORT = env("ACTIVEMQ_WEB_CONSOLE_PORT", default=8161)
ACTIVEMQ_OPENWIRE_PORT = env("ACTIVEMQ_OPENWIRE_PORT", default=61616)
ACTIVEMQ_STOMP_PORT = env("ACTIVEMQ_STOMP_PORT", default=61613)
ACTIVEMQ_MQTT_PORT = env("ACTIVEMQ_MQTT_PORT", default=1883)
ACTIVEMQ_AMQP_PORT = env("ACTIVEMQ_AMQP_PORT", default=5672)

# ElasticSearch
ELASTICSEARCH_HOST = env("ELASTICSEARCH_HOST", default="localhost")
ELASTICSEARCH_PORT = env("ELASTICSEARCH_PORT", default=9200)
ELASTICSEARCH_DSL = {
    "default": {
        "hosts": [f"http://{ELASTICSEARCH_HOST}:{ELASTICSEARCH_PORT}/"],
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
    "django_crontab",
    "django_filters",
    "bandit",
    "django_nose",
)
LOCAL_APPS = (
    "users",
)
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
        # 'core.authentications.APIAuthentication',
    ],
    "DEFAULT_PAGINATION_CLASS": "core.common.BasePagination",
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
        "HOST": "127.0.0.1",
        "PORT": "3306",
        "OPTIONS": {
            "init_command": "SET GLOBAL max_connections = 100000",
            "charset": "utf8mb4",
        },
    }


DATABASES = {
    "default": db_config(),
}

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
USE_TZ = False

# https://docs.djangoproject.com/en/2.2/howto/static-files/
STATIC_URL = "/static/"
