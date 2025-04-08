from typing import Callable

from src import rabbitmq_manager


class RabbitAdapter:
    def __init__(self):
        self.rabbit = rabbitmq_manager

    async def send_message(self, queue_name: str, message: Callable):
        await self.rabbit.publish(queue_name, message)

    async def receive_message(self, queue_name, function):
        await self.rabbit.start_consumer(queue_name, function)
