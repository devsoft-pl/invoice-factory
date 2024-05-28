from .common import *  # noqa: F403, F401 isort:skip

ALLOWED_HOSTS = ["invoice-factory.devsoft.pl"]

DEFAULT_FILE_STORAGE = "base.storages.MediaStorage"
STATICFILES_STORAGE = "base.storages.StaticStorage"

DEBUG = False

CSRF_TRUSTED_ORIGINS = [f"https://invoice-factory.devsoft.pl"]

CORS_ALLOWED_ORIGINS = [
    "https://invoice-factory.devsoft.pl",
]
