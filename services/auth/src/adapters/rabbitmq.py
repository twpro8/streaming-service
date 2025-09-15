import json

from pydantic import BaseModel

from src.connectors.rabbit_conn import RabbitManager


class RabbitAdapter:
    def __init__(self, rabbit: RabbitManager, exchange_name: str):
        self.rabbit = rabbit
        self.exchange_name = exchange_name

    async def publish_to_exchange(self, event: str, message: BaseModel | dict):
        """
        Publishes a message about a specific event to exchange
        Examples:
        Exchange name — "events"
        Event — "v1.film.created" => "version.subject.event"
        Message — {"id": 123}
        """
        if isinstance(message, BaseModel):
            message = message.model_dump()

        await self.rabbit.publish_to_exchange(
            exchange_name=self.exchange_name,
            routing_key=event,
            message=json.dumps(message),
        )

    async def publish_to_queue(self):
        """
        Publish directly to queue
        """
        pass
