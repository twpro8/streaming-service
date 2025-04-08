import time

from src.db import DBManager, null_pool_session_maker
from src.tasks.celery_app import celery_instance


@celery_instance.task
def test_task():
    time.sleep(1)
    print(" [*] CELERY [*] The job is done!")


async def on_film_delete(film_id):
    async with DBManager(session_factory=null_pool_session_maker) as db:
        film_id = int(film_id)
        await db.favorites.delete(film_id=film_id)
