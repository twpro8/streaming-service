from celery import Celery
from celery.schedules import crontab

from src.config import settings


app = Celery("tasks", broker=settings.REDIS_URL, include=["src.tasks.tasks"])
app.conf.beat_schedule = {
    "delete-inactive-users-every-24-hours": {
        "task": "src.tasks.tasks.delete_inactive_users_task",
        "schedule": crontab(hour=0, minute=0),
    },
    "delete-expired-refresh-tokens-every-24-hours": {
        "task": "src.tasks.tasks.delete_expired_refresh_tokens_task",
        "schedule": crontab(hour=1, minute=0),
    },
}
app.conf.timezone = "UTC"
app.conf.enable_utc = True
