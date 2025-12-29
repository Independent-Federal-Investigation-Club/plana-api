import os
from enum import Enum
from typing import Optional
from datetime import datetime, timezone

import redis.asyncio as aioredis

from loguru import logger
from pydantic import BaseModel, Field

from plana.database.models.message import Message


class PlanaEvents(str, Enum):
    """Message event types for Redis pub/sub."""

    MESSAGE_CREATE = "MESSAGE_CREATE"
    MESSAGE_UPDATE = "MESSAGE_UPDATE"
    MESSAGE_DELETE = "MESSAGE_DELETE"
    COMMAND_REGISTER = "COMMAND_REGISTER"
    COMMAND_UNREGISTER = "COMMAND_UNREGISTER"
    GUILD_CONFIG_REFRESH = "GUILD_CONFIG_REFRESH"


class GuildConfigEventData(BaseModel):
    """Event data for command registration and unregistration."""

    name: str


class EventPayload(BaseModel):
    """Event data wrapper for event events."""

    event: PlanaEvents
    guild_id: int
    data: Optional[Message | GuildConfigEventData] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        use_enum_values = True


class RedisEventPublisher:
    """
    Redis publisher for events events.

    Simple, focused class that only handles publishing events.
    """

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client: Optional[aioredis.Redis] = None

    async def connect(self) -> None:
        """Connect to aioredis."""
        if self.redis_client is None:
            self.redis_client = aioredis.from_url(self.redis_url)
            logger.info("Publisher connected to Redis")

    async def disconnect(self) -> None:
        """Disconnect from aioredis."""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Publisher disconnected from Redis")

    async def publish_message_event(
        self, data: Message | None, event_type: PlanaEvents
    ) -> None:
        """Publish a events creation event."""

        if not data:
            return

        if self.redis_client is None:
            await self.connect()

        if not event_type.value.startswith("MESSAGE_"):
            raise ValueError("Invalid event type for events publishing")

        event_data = EventPayload(event=event_type, data=data, guild_id=data.guild_id)
        await self.publish_event(event_data)

    async def publish_event(self, event_data: EventPayload) -> None:
        """Internal method to publish events."""
        if not self.redis_client:
            await self.connect()

        logger.info(
            f"Publishing event: {event_data.event} for guild {event_data.guild_id}"
        )

        channel = f"events:{event_data.guild_id}"
        events = event_data.model_dump_json(exclude_unset=True)

        await self.redis_client.publish(channel, events)

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()


def get_redis_url() -> str:
    """
    Get the Redis URL from environment variables.
    """
    from dotenv import load_dotenv

    load_dotenv()

    url = os.getenv("REDIS_URL")
    password = os.getenv("PLANA_PASSWORD")

    return f"redis://:{password}@{url}" if password else url or "redis://localhost:6379"


PUB = RedisEventPublisher(redis_url=get_redis_url())
