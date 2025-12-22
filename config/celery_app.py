import os

from celery import Celery
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
app = Celery("Hober bank")

app.config_from_object("django.conf:settings", namespace="Celery")

app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
