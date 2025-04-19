import logging

from typing import Callable
import asyncio

from aio_pika import connect_robust, Message, DeliveryMode, IncomingMessage


log = logging.getLogger(__name__)


class RabbitManager:
    def __init__(self, amqp_url: str):
        self.amqp_url = amqp_url
        self.connection = None
        self.channel = None

    async def connect(self):
        """Creates an asynchronous connection with RabbitMQ"""
        if not self.connection or self.connection.is_closed:
            log.info("RabbitMQ: Connecting...")
            try:
                self.connection = await connect_robust(self.amqp_url)
                self.channel = await self.connection.channel()
                log.info("RabbitMQ: Connected")
            except Exception as e:
                log.error(f"RabbitMQ: Failed to connect: {e}")
                log.info("RabbitMQ: Retying to connect in 5 seconds")
                await asyncio.sleep(5)
                await self.connect()

    async def close(self):
        """Closes the connection to RabbitMQ"""
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
            log.info("RabbitMQ: Connection closed")

    async def publish(self, queue_name: str, message: str):
        """Publishes a message to a RabbitMQ queue"""
        queue = await self.channel.declare_queue(queue_name, durable=True)
        await self.channel.default_exchange.publish(
            Message(body=message.encode(), delivery_mode=DeliveryMode.PERSISTENT),
            routing_key=queue.name,
        )
        log.info(f"RabbitMQ: Sent message to queue {queue_name}: {message}")

    async def consume(self, queue_name: str, callback: Callable):
        """Launches an asynchronous consumer"""
        queue = await self.channel.declare_queue(queue_name, durable=True)

        async def wrapper(message: IncomingMessage):
            async with message.process():
                log.info(f"RabbitMQ: Received message: {message.body.decode()}")
                try:
                    await callback(message.body.decode())
                except Exception as e:
                    log.error(f"RabbitMQ: Error processing message: {e}. Retrying in 5 seconds...")
                    await asyncio.sleep(5)
                    await message.nack(requeue=True)

        await queue.consume(wrapper)
        log.info(f"RabbitMQ: Listening on queue: {queue_name}")
        await asyncio.Future()  # Keeping the process going

    async def start_consumer(self, queue_name: str, callback: Callable):
        """Launches the consumer in a separate asyncio Task"""
        asyncio.create_task(self.consume(queue_name, callback))
        log.info(f"RabbitMQ: Consumer started for queue {queue_name}")
