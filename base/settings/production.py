from .common import *  # noqa: F403, F401 isort:skip

ALLOWED_HOSTS = ["invoice-factory.devsoft.pl"]


STORAGES = {
    "default": {
        "BACKEND": "base.storages.MediaStorage",
    },
    "staticfiles": {
        "BACKEND": "base.storages.StaticStorage",
    },
}

DEBUG = False

CSRF_TRUSTED_ORIGINS = ["https://invoice-factory.devsoft.pl"]

CORS_ALLOWED_ORIGINS = [
    "https://invoice-factory.devsoft.pl",
]
