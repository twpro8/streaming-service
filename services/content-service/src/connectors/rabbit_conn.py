from typing import Callable
import asyncio

from aio_pika import connect_robust, Message, DeliveryMode, IncomingMessage

from src.config import settings


class RabbitManager:
    def __init__(self):
        self.amqp_url = settings.RABBITMQ_URL
        self.connection = None
        self.channel = None

    async def connect(self):
        """Creates an asynchronous connection with RabbitMQ"""
        if not self.connection or self.connection.is_closed:
            self.connection = await connect_robust(self.amqp_url)
            self.channel = await self.connection.channel()
            print("Connected to RabbitMQ")

    async def close(self):
        """Closes the connection to RabbitMQ"""
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
            print("RabbitMQ connection closed")

    async def publish(self, queue_name: str, message: str):
        """Publishes a message to a RabbitMQ queue"""
        await self.connect()
        queue = await self.channel.declare_queue(queue_name, durable=True)
        await self.channel.default_exchange.publish(
            Message(body=message.encode(), delivery_mode=DeliveryMode.PERSISTENT),
            routing_key=queue.name,
        )
        print(f"Sent message to queue {queue_name}: {message}")

    async def consume(self, queue_name: str, callback: Callable):
        """Launches an asynchronous consumer"""
        await self.connect()
        queue = await self.channel.declare_queue(queue_name, durable=True)

        async def wrapper(message: IncomingMessage):
            async with message.process():
                print(f"Received message: {message.body.decode()}")
                await callback(message.body.decode())

        await queue.consume(wrapper)
        print(f"Listening on queue: {queue_name}")
        await asyncio.Future()  # Keeping the process going

    async def start_consumer(self, queue_name: str, callback: Callable):
        """Launches the consumer in a separate asyncio Task"""
        asyncio.create_task(self.consume(queue_name, callback))
        print(f"Consumer started for queue {queue_name}")
