import os
import django
from celery import Celery
from celery.schedules import crontab

django.setup()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

app = Celery("config")

app.config_from_object("django.conf:settings", namespace="CELERY")

# app.conf.broker_url = "redis://localhost:6379/0"  # Hardcoded for testing
# app.conf.result_backend = "redis://localhost:6379/0"

app.autodiscover_tasks()

app.conf.beat_schedule = {
    "broadcast_company_metrics": {
        "task": "apps.companies.tasks.broadcast_company_metrics",
        "schedule": crontab(minute="*/1"),
    },
}