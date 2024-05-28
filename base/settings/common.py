import os
from pathlib import Path

import environ
from celery.schedules import crontab
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

env = environ.Env(DEBUG=(bool, False), EMAIL_USE_TLS=(bool, False))

BASE_DIR = Path(__file__).resolve().parent.parent.parent

environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

SECRET_KEY = env("SECRET_KEY")

DEBUG = env("DEBUG")

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django_filters",
    "django_extensions",
    "factory_generator",
    "rest_framework",
    "rest_framework.authtoken",
    "corsheaders",
    "invoices",
    "companies",
    "countries",
    "currencies",
    "vat_rates",
    "items",
    "users",
    "reports",
    "accountants",
    "summary_recipients",
    "persons",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "base.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 10,
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.TokenAuthentication",
    ],
}

WSGI_APPLICATION = "base.wsgi.application"

DATABASES = {
    "default": env.db(),
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation."
        "UserAttributeSimilarityValidator",
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

LANGUAGE_CODE = "pl"
TIME_ZONE = "Europe/Warsaw"
USE_TZ = True
USE_I18N = True
USE_L10N = True
USE_THOUSAND_SEPARATOR = True
THOUSAND_SEPARATOR = "$"

LOCALE_PATHS = (os.path.join(BASE_DIR, "locale"),)

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

MEDIA_BUCKET_NAME = env("MEDIA_BUCKET_NAME", default=None)
MEDIA_ENDPOINT_URL = env("MEDIA_ENDPOINT_URL", default=None)

STATIC_BUCKET_NAME = env("STATIC_BUCKET_NAME", default=None)
STATIC_ENDPOINT_URL = env("STATIC_ENDPOINT_URL", default=None)

AWS_S3_CUSTOM_DOMAIN = env("AWS_S3_CUSTOM_DOMAIN", default=None)
MEDIA_CUSTOM_DOMAIN = env("MEDIA_CUSTOM_DOMAIN", default=None)
STATIC_CUSTOM_DOMAIN = env("STATIC_CUSTOM_DOMAIN", default=None)
AWS_S3_REGION_NAME = env("AWS_S3_REGION_NAME", default=None)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

EMAIL_HOST = env("EMAIL_HOST", default="")
EMAIL_PORT = env("EMAIL_PORT", default="")
EMAIL_HOST_USER = env("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = env("EMAIL_USE_TLS")

AWS_ACCESS_KEY_ID = env(  # noqa: F405
    "AWS_ACCESS_KEY_ID", default="minio_root_user"
)  # noqa: F405
AWS_SECRET_ACCESS_KEY = env(  # noqa: F405
    "AWS_SECRET_ACCESS_KEY", default="minio_root_password"
)

CELERY_BROKER_URL = env("CELERY_BROKER_URL", default="")

CELERY_BEAT_SCHEDULE = {
    "create-recurring-invoices": {
        "task": "create_invoices_for_recurring",
        "schedule": crontab(minute="0", hour="6"),
    },
    "send-summary-recipients": {
        "task": "send_monthly_summary_to_recipients",
        "schedule": crontab(minute="0", hour="7"),
    },
    "get-exchange-rates-from-nbp": {
        "task": "get_exchange_rates_for_all",
        "schedule": crontab(minute="0", hour="9"),
    },
}

LOGIN_URL = "users:login"

TEST_RUNNER = "base.runner.PytestTestRunner"

EMAIL_SENDER = env("EMAIL_SENDER", default="")

CEIDG_API_TOKEN = env("CEIDG_API_TOKEN", default="")

AUTH_USER_MODEL = "users.User"

CORS_ORIGIN_WHITELIST = ["http://localhost:3000"]

SENTRY_DSN = env("SENTRY_DSN", default=None)

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=1.0,
        # If you wish to associate users to errors (assuming you are using
        # django.contrib.auth) you may enable sending PII data.
        send_default_pii=True,
    )
