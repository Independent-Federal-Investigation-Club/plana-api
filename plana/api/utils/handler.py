from typing import Optional, Union

from fastapi import HTTPException, status

from plana.database.models.message import Message, Messages, PlanaDBModel
from plana.database.utils.pub import (
    PUB,
    EventPayload,
    GuildConfigEventData,
    PlanaEvents,
)


def raise_404_if_not_found(item: "PlanaDBModel"):
    """Generic function to raise an HTTPException if an item is not found."""
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Resource not found",
        )


async def manage_message_state_change(
    old_message: Union[Message, Messages, dict],
    new_message: Optional[Union[Message, Messages, dict]] = bool,
):
    """
    Handle message publish event on state change

    Args:
        old_message (Union[Message, Messages, dict]): The previous state of the message.
        new_message (Optional[Union[Message, Messages, dict]]): The new state of the message.

    Returns:
        bool: True if a message event was published, False otherwise.
    """

    # Convert old_message to Message if it's a Messages ORM instance
    if isinstance(old_message, Messages):
        old_message = Message.model_validate(old_message.to_dict())
    elif isinstance(old_message, dict):
        old_message = Message.model_validate(old_message)

    if new_message and isinstance(new_message, Messages):
        new_message = Message.model_validate(new_message.to_dict())
    elif new_message and isinstance(new_message, dict):
        new_message = Message.model_validate(new_message)

    old_published = bool(old_message.published) if old_message else False
    new_published = bool(new_message.published) if new_message else False

    if new_message and new_message.channel_id is None:
        # If the message has no channel, do not publish any message events
        return False

    if new_published and not old_published:
        # If the message is being updated from unpublished to published, or
        # if the message is being created with a published state, publish the creation event
        await PUB.publish_message_event(new_message, PlanaEvents.MESSAGE_CREATE)
        return True

    elif new_published and old_published:
        # If the message is already published, just update it
        await PUB.publish_message_event(new_message, PlanaEvents.MESSAGE_UPDATE)
        return False

    elif old_published and not new_published:
        # If the message is being unpublished, publish a deletion event
        await PUB.publish_message_event(old_message, PlanaEvents.MESSAGE_DELETE)
        return False


async def handle_guild_config_refresh(guild_id: int, setting_name: str):
    """
    Handle guild setting refresh event.

    Args:
        guild_id (int): The ID of the guild.
        setting_name (str): The name of the setting being refreshed.

    Returns:
        None
    """
    await PUB.publish_event(
        event_data=EventPayload(
            event=PlanaEvents.GUILD_CONFIG_REFRESH,
            guild_id=guild_id,
            data=GuildConfigEventData(name=setting_name),
        )
    )
