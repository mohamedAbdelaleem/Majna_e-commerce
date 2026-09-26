import os
from celery import Celery
from celery.beat import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "majna.settings")
app = Celery("celery_app")
app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks(["majna"])

app.conf.beat_schedule = {
    "cleanup_expired_tokens": {
        "task": "majna.tasks.cleanup_expired_tokens",
        "schedule": crontab(day_of_week="fri", hour=1, minute=0),
    }
}
