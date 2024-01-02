import os

import environ

from django.utils.translation import gettext_lazy as __

from ._setup import APPS_DIR, BASE_DIR, PLUGGABLE_FUNCS, clean_ellipsis, env, log_ignore_modules

# Set defaults
defaults = {}
if env("DATABASE_URL", default=None) is None:
    defaults.update(
        DATABASE_URL=(
            (
                str,
                f"postgres://{env.str('POSTGRES_USER', '')}:{env.str('POSTGRES_PASSWORD', '')}@{env.str('POSTGRES_HOST', '')}:{env.int('POSTGRES_PORT', 0)}/{env.str('POSTGRES_DB', '')}",  # noqa: E501
            )
        )
    )
env = environ.Env(**defaults)
# SECURITY
# ------------------------------------------------------------------------------
DEBUG = env.bool("DJANGO_DEBUG", False)
SECRET_KEY = env.str("DJANGO_SECRET_KEY")
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "0.0.0.0", "127.0.0.1"])
CSRF_TRUSTED_ORIGINS = [f"https://{i}" for i in ALLOWED_HOSTS]
INTERNAL_IPS = ["127.0.0.1", "10.0.2.2"]
if env("USE_DOCKER") == "yes":
    import socket

    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS += [".".join(ip.split(".")[:-1] + ["1"]) for ip in ips]
SECURE_PROXY_SSL_HEADER = env.tuple("DJANGO_SECURE_PROXY_SSL_HEADER", default=("HTTP_X_FORWARDED_PROTO", None))
SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=False)
SESSION_COOKIE_SECURE = env.bool("DJANGO_SESSION_COOKIE_SECURE", default=False)
CSRF_COOKIE_SECURE = env.bool("DJANGO_CSRF_COOKIE_SECURE", default=False)
SECURE_HSTS_SECONDS = env.int("DJANGO_SECURE_HSTS_SECONDS", default=0)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", default=False)
SECURE_HSTS_PRELOAD = env.bool("DJANGO_SECURE_HSTS_PRELOAD", default=False)
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False
X_FRAME_OPTIONS = "DENY"

# GENERAL
# ------------------------------------------------------------------------------
ROOT_URLCONF = "config.urls"
ASGI_APPLICATION = "config.asgi.application"
WSGI_APPLICATION = "config.wsgi.application"

# I18N and L10N
# ------------------------------------------------------------------------------
TIME_ZONE = "UTC"
LANGUAGE_CODE = "en-us"
LANGUAGES = [
    ("en", __("English")),
    ("fa", __("Persian")),
    ("ar", __("Arabic")),
]
USE_I18N = True
USE_TZ = True
LOCALE_PATHS = [str(BASE_DIR / "locale")]

# DATABASES
# ------------------------------------------------------------------------------
DATABASES = {"default": env.db("DATABASE_URL")}
DATABASES["default"]["CONN_MAX_AGE"] = env.int("CONN_MAX_AGE", default=0)
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# CACHES
# ------------------------------------------------------------------------------
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("REDIS_URL"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            # Mimicing memcache behavior.
            "IGNORE_EXCEPTIONS": True,
        },
    }
}

# APPS
# ------------------------------------------------------------------------------
LOCAL_APPS = [
    "name_goes_here.users",
]
THIRD_PARTY_APPS = clean_ellipsis(
    [
        "corsheaders",
        "debug_toolbar" if PLUGGABLE_FUNCS.DEBUG_TOOLBAR else ...,
        "django_celery_beat",
        "django_filters",
        "drf_spectacular",
        "graphene_django",
        "graphql_jwt.refresh_token",
        "rest_framework",
        "rest_framework_simplejwt",
        "whitenoise.runserver_nostatic",
        # make sure any runserver command is after whitenoise's
        "daphne" if PLUGGABLE_FUNCS.DAPHNE else ...,
    ]
)
DJANGO_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.admin",
    "django.forms",
]
INSTALLED_APPS = LOCAL_APPS + THIRD_PARTY_APPS + DJANGO_APPS

# AUTHENTICATION
# ------------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = [
    "graphql_jwt.backends.JSONWebTokenBackend",
    "django.contrib.auth.backends.ModelBackend",
]
AUTH_USER_MODEL = "users.User"
LOGIN_REDIRECT_URL = "users:redirect"
LOGIN_URL = "account_login"

# PASSWORDS
# ------------------------------------------------------------------------------
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
]
AUTH_PASSWORD_VALIDATORS = (
    [
        {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
        {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
        {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
        {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
    ]
    if not PLUGGABLE_FUNCS.NO_PASS_VALIDATION
    else []
)

# MIDDLEWARE
# ------------------------------------------------------------------------------
MIDDLEWARE = clean_ellipsis(
    [
        "debug_toolbar.middleware.DebugToolbarMiddleware" if PLUGGABLE_FUNCS.DEBUG_TOOLBAR else ...,
        "django.middleware.security.SecurityMiddleware",
        "corsheaders.middleware.CorsMiddleware",
        "whitenoise.middleware.WhiteNoiseMiddleware" if PLUGGABLE_FUNCS.SERVE_STATICFILES else ...,
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.locale.LocaleMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
    ]
)

# STATIC
# ------------------------------------------------------------------------------
STATIC_ROOT = str(BASE_DIR / "staticfiles")
STATIC_URL = "/static/"
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

# MEDIA
# ------------------------------------------------------------------------------
MEDIA_ROOT = str(APPS_DIR / "media")
MEDIA_URL = "/media/"

# TEMPLATES
# ------------------------------------------------------------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [str(APPS_DIR / "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

# FIXTURES
# ------------------------------------------------------------------------------
FIXTURE_DIRS = (str(APPS_DIR / "fixtures"),)

# ADMIN
# ------------------------------------------------------------------------------
# Django Admin URL.
ADMIN_URL = env.str("DJANGO_ADMIN_URL", "admin/")
# https://docs.djangoproject.com/en/dev/ref/settings/#admins

# TESTING
# ------------------------------------------------------------------------------
# The name of the class to use to run the test suite
TEST_RUNNER = "django.test.runner.DiscoverRunner"

# LOGGING
# ------------------------------------------------------------------------------
logs_dir = os.path.join(BASE_DIR, "logs")
os.makedirs(logs_dir, exist_ok=True)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {
        "ignore_autoreload": {"()": "django.utils.log.CallbackFilter", "callback": log_ignore_modules(["autoreload"])}
    },
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "level": "INFO",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": os.path.join(logs_dir, "info.log"),
            "backupCount": env.int("MAX_LOG_FILE_COUNT", default=1),
            "maxBytes": 50 * 1024 * 1024,
            "filters": ["ignore_autoreload"],
            "formatter": "verbose",
        },
    },
    "root": {"level": "INFO", "handlers": ["console", "file"]},
}
