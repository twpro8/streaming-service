from celery import Celery

from src.config import settings


app = Celery("tasks", broker=settings.REDIS_URL, include=["src.tasks.tasks"])
