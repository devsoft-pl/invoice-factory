import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "base.settings.dev")

app = Celery("invoice_manager")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
