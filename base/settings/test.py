from .common import *  # noqa: F403, F401 isort:skip


# DEFAULT_FILE_STORAGE = "base.storages.MediaStorage"
# STATICFILES_STORAGE = "base.storages.StaticStorage"
DATABASES["default"] = {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": ":memory:",
}

DEBUG = True
LANGUAGE_CODE = "en-us"
