import time

from src.tasks.celery_app import celery_instance

@celery_instance.task
def test_task():
    time.sleep(1)
    print(" [*] CELERY [*] The job is done!")
