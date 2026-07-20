"""Django settings for the Papasmurfs project."""

import os
from pathlib import Path

import dj_database_url
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

# Load local environment variables from the project-root .env file.
# Deployment platforms normally provide these variables directly.
load_dotenv(BASE_DIR / ".env")


def get_boolean_environment_variable(name, default=False):
    """Convert a common environment-variable string into a Boolean."""

    value = os.getenv(name)

    if value is None:
        return default

    return value.strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def get_list_environment_variable(name, default=None):
    """Convert a comma-separated environment variable into a list."""

    value = os.getenv(name)

    if not value:
        return default or []

    return [
        item.strip()
        for item in value.split(",")
        if item.strip()
    ]


# ---------------------------------------------------------------------
# Core security settings
# ---------------------------------------------------------------------

DEBUG = get_boolean_environment_variable(
    "DJANGO_DEBUG",
    True,
)

SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-local-development-only-not-for-production",
)

if (
    not DEBUG
    and SECRET_KEY.startswith("django-insecure-")
):
    raise RuntimeError(
        "A secure DJANGO_SECRET_KEY environment variable is required "
        "when DJANGO_DEBUG is False."
    )


ALLOWED_HOSTS = get_list_environment_variable(
    "DJANGO_ALLOWED_HOSTS",
    [
        "127.0.0.1",
        "localhost",
    ]
    if DEBUG
    else [],
)

CSRF_TRUSTED_ORIGINS = get_list_environment_variable(
    "DJANGO_CSRF_TRUSTED_ORIGINS",
)


# ---------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    "core",
    "catalogue",
    "accounts",
    "controlpanel",
    "searchapp",
    "dashboard",
    "cart",
    "orders.apps.OrdersConfig",
    "ratings",
    "recommendations",
    "usermanagement",
]


# ---------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    # WhiteNoise must appear directly after SecurityMiddleware.
    "whitenoise.middleware.WhiteNoiseMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "config.urls"


# ---------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------

TEMPLATES = [
    {
        "BACKEND": (
            "django.template.backends.django.DjangoTemplates"
        ),
        "DIRS": [
            BASE_DIR / "templates",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                (
                    "django.template.context_processors.request"
                ),
                (
                    "django.contrib.auth.context_processors.auth"
                ),
                (
                    "django.contrib.messages.context_processors.messages"
                ),
            ],
        },
    },
]


WSGI_APPLICATION = "config.wsgi.application"


# ---------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "",
).strip()

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=not DEBUG,
        ),
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        },
    }


# ---------------------------------------------------------------------
# Password validation
# ---------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth.password_validation."
            "NumericPasswordValidator"
        ),
    },
]


# ---------------------------------------------------------------------
# Internationalisation
# ---------------------------------------------------------------------

LANGUAGE_CODE = "en-us"

TIME_ZONE = os.getenv(
    "DJANGO_TIME_ZONE",
    "Europe/Athens",
)

USE_I18N = True

USE_TZ = True


# ---------------------------------------------------------------------
# Authentication navigation
# ---------------------------------------------------------------------

LOGIN_URL = "accounts:login"

LOGIN_REDIRECT_URL = "dashboard:home"

LOGOUT_REDIRECT_URL = "core:home"


# ---------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------

STATIC_URL = "/static/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
]

STATIC_ROOT = BASE_DIR / "staticfiles"

STORAGES = {
    "default": {
        "BACKEND": (
            "django.core.files.storage.FileSystemStorage"
        ),
    },
    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage."
            "CompressedManifestStaticFilesStorage"
        ),
    },
}


# ---------------------------------------------------------------------
# User-uploaded media
# ---------------------------------------------------------------------

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "media"


# ---------------------------------------------------------------------
# Production security
# ---------------------------------------------------------------------

# Common deployment services place Django behind a secure reverse proxy.
SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)

SECURE_SSL_REDIRECT = (
    not DEBUG
    and get_boolean_environment_variable(
        "DJANGO_SECURE_SSL_REDIRECT",
        True,
    )
)

SESSION_COOKIE_SECURE = not DEBUG

CSRF_COOKIE_SECURE = not DEBUG

SESSION_COOKIE_HTTPONLY = True

SECURE_HSTS_SECONDS = (
    0
    if DEBUG
    else int(
        os.getenv(
            "DJANGO_SECURE_HSTS_SECONDS",
            "3600",
        )
    )
)

SECURE_HSTS_INCLUDE_SUBDOMAINS = (
    not DEBUG
    and get_boolean_environment_variable(
        "DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS",
        False,
    )
)

SECURE_HSTS_PRELOAD = (
    not DEBUG
    and get_boolean_environment_variable(
        "DJANGO_SECURE_HSTS_PRELOAD",
        False,
    )
)

SECURE_CONTENT_TYPE_NOSNIFF = True

SECURE_REFERRER_POLICY = "same-origin"

X_FRAME_OPTIONS = "DENY"


DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
