import asyncio

import logging as log
from typing import Callable

from aio_pika import connect_robust, Message, DeliveryMode, IncomingMessage


log.basicConfig(level=log.INFO)


class RabbitManager:
    def __init__(self, amqp_url: str):
        self.amqp_url = amqp_url
        self.connection = None
        self.channel = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def connect(self):
        if not self.connection or self.connection.is_closed:
            try:
                self.connection = await connect_robust(url=self.amqp_url)
                self.channel = await self.connection.channel()
            except Exception as e:
                log.error(f"RabbitMQ: Failed to connect: {e}")
                log.info("RabbitMQ: Retying to connect in 5 seconds")
                await asyncio.sleep(5)
                await self.connect()

    async def close(self):
        if self.connection and not self.connection.is_closed:
            await self.connection.close()

    async def start_consuming_from_exchange(
        self, exchange_name: str, queue_name: str, routing_key: str, callback: Callable
    ):
        exchange = await self.channel.declare_exchange(
            name=exchange_name, type="topic", durable=True
        )
        queue = await self.channel.declare_queue(name=queue_name, durable=True)

        await queue.bind(exchange=exchange, routing_key=routing_key)

        log.info(f'RabbitMQ: Waiting for exchange "{exchange_name}". To exit press CTRL+C')

        async def wrapper(message: IncomingMessage):
            try:
                await callback(message)
                await message.ack()
            except Exception as e:
                await message.nack(requeue=True)
                log.exception(f"RabbitMQ: Error: {e}")
                raise

        await queue.consume(callback=wrapper, no_ack=False)

    async def publish_to_exchange(self, exchange_name: str, routing_key: str, message: str):
        await self.connect()
        exchange = await self.channel.declare_exchange(
            name=exchange_name, type="topic", durable=True
        )

        await exchange.publish(
            Message(
                body=message.encode(),
                delivery_mode=DeliveryMode.PERSISTENT,
            ),
            routing_key=routing_key,
        )

        log.info(
            f'RabbitMQ: Sent to exchange "{exchange_name}" with routing key "{routing_key}" message "{message}"'
        )
        await self.close()
