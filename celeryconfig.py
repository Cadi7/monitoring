import os

from celery import Celery

from config import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
app = Celery(broker=settings.CELERY_BROKER_URL, include=['apps.monitoring.tasks'])

app.config_from_object("config.settings", namespace="CELERY")
app.autodiscover_tasks()
