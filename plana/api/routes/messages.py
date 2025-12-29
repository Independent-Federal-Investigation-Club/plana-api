from typing import Optional
from loguru import logger
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request

from plana.api.middleware.utils import bot_only_operation
from plana.api.utils.helper import (
    _handle_database_error,
    ids_string_to_int,
)
from plana.api.utils.handler import raise_404_if_not_found
from plana.database.models.message import Messages, Message


MESSAGE_ROUTER = APIRouter()


@MESSAGE_ROUTER.post("/")
async def create_message(
    message_data: Message,
    _: None = Depends(bot_only_operation),
):
    """Create a new message for the guild"""
    try:
        create_data = message_data.model_dump(exclude_unset=True)

        message = Messages(**create_data)
        await message.save()

        message_data.id = message.id  # Ensure id is set after save

        return message.to_dict()
    except Exception as e:
        raise _handle_database_error("create message", e)


@MESSAGE_ROUTER.get("/")
async def list_messages(
    guild_id: str = Query(..., description="Guild ID"),
    limit: Optional[int] = Query(
        default=50, le=100, description="Maximum number of messages to return"
    ),
    offset: Optional[int] = Query(
        default=0, ge=0, description="Number of messages to skip"
    ),
    _: None = Depends(bot_only_operation),
):
    """List all messages for a guild"""
    guild_id_int = ids_string_to_int(guild_id=guild_id)
    try:
        messages = await Messages.filter(
            Messages.guild_id == guild_id_int,
            limit=limit,
            offset=offset,
            order_by=Messages.updated_at.desc(),
        )
        total_count = await Messages.count(Messages.guild_id == guild_id_int)

        return {
            "data": [message.to_dict() for message in messages],
            "total": total_count,
        }
    except Exception as e:
        raise _handle_database_error("fetch guild messages", e)


@MESSAGE_ROUTER.get("/{id}")
async def get_message(
    id: str = Path(..., description="Message ID"),
    _: None = Depends(bot_only_operation),
):
    """Get a specific message"""
    id_int = ids_string_to_int(id=id)
    try:
        message = await Messages.get(id_int)
        raise_404_if_not_found(message)

        return message.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise _handle_database_error("fetch message", e)


@MESSAGE_ROUTER.put("/{id}")
@MESSAGE_ROUTER.patch("/{id}")
async def update_message(
    request: Request,
    message_data: Message,
    id: str = Path(..., description="Message ID"),
    _: None = Depends(bot_only_operation),
):
    """Update a specific message"""
    id_int = ids_string_to_int(id=id)
    try:
        logger.info(f"Updating message {id} with data: {message_data}")
        message = await Messages.get(id_int)
        raise_404_if_not_found(message)

        if request.method == "PUT":
            update_data = message_data.model_dump(
                exclude={"id", "guild_id", "updated_at"}
            )
        else:
            # Only update fields that are provided in the PATCH request
            update_data = message_data.model_dump(
                exclude={"id", "guild_id", "updated_at"}, exclude_unset=True
            )

        await message.update(**update_data)
        return message.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise _handle_database_error("update message", e)


@MESSAGE_ROUTER.delete("/{id}")
async def delete_message(
    id: str = Path(..., description="Message ID"),
    _: None = Depends(bot_only_operation),
):
    """Delete a specific message"""
    id_int = ids_string_to_int(id=id)
    try:
        message = await Messages.get(id_int)
        raise_404_if_not_found(message)

        await message.delete()

        logger.info(f"Deleted message {id} for guild {message.guild_id}")
        return {"message": "Message deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise _handle_database_error("delete message", e)
