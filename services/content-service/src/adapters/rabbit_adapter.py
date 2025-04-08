import json
from typing import Callable

from src import rabbitmq_manager


class RabbitAdapter:
    def __init__(self):
        self.rabbit = rabbitmq_manager

    async def send_message(self, queue_name: str, message):
        await self.rabbit.publish(queue_name, message)

    async def receive_message(self, queue_name, function: Callable):
        await self.rabbit.start_consumer(queue_name, function)

    async def film_deletion(self, film_id: int):
        message_json = {"film_id": film_id}
        message_body = json.dumps(message_json)
        await self.send_message("film_deletion", message_body)
