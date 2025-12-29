from typing import Optional
from loguru import logger
from fastapi import APIRouter, Depends, HTTPException, Path, Query

from plana.api.middleware.utils import require_permission
from plana.api.utils.helper import (
    _handle_database_error,
    ids_string_to_int,
)
from plana.api.utils.handler import (
    manage_message_state_change,
    raise_404_if_not_found,
)
from plana.database.models.message import Messages, Message


router = APIRouter()


@router.get("/{guild_id}/messages")
async def list_guild_messages(
    guild_id: str = Path(..., description="Discord Guild ID"),
    limit: Optional[int] = Query(
        default=50, le=100, description="Maximum number of messages to return"
    ),
    offset: Optional[int] = Query(
        default=0, ge=0, description="Number of messages to skip"
    ),
    _: None = Depends(require_permission),
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
    except HTTPException:
        raise
    except Exception as e:
        raise _handle_database_error("fetch guild messages", e)


@router.get("/{guild_id}/messages/{message_id}")
async def get_message(
    guild_id: str = Path(..., description="Discord Guild ID"),
    message_id: str = Path(..., description="Discord Message ID"),
    _: None = Depends(require_permission),
):
    """Get a specific message"""
    ids = ids_string_to_int(guild_id=guild_id, message_id=message_id)
    guild_id_int, message_id_int = ids if isinstance(ids, tuple) else (ids, ids)

    try:
        message = await Messages.get_by(guild_id=guild_id_int, id=message_id_int)
        raise_404_if_not_found(message)

        return message.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise _handle_database_error("fetch message", e)


@router.post("/{guild_id}/messages")
async def create_message(
    message_data: Message,
    guild_id: str = Path(..., description="Discord Guild ID"),
    _: None = Depends(require_permission),
):
    """Create a new message for the guild"""
    guild_id_int = ids_string_to_int(guild_id=guild_id)

    try:
        create_data = message_data.model_dump(exclude={"guild_id"}, exclude_unset=True)
        message = Messages(guild_id=guild_id_int, **create_data)
        await message.save()

        message_data.id = message.id
        created = await manage_message_state_change(
            old_message=None,
            new_message=message_data,
        )

        if not created:
            return message.to_dict()

        # Ensure the message is saved with the correct message_id
        message = await message.refresh_until_message_id()
        if message.message_id is None:
            message.published = False
        return message.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise _handle_database_error("create message", e)


@router.put("/{guild_id}/messages/{message_id}")
async def update_message(
    message_data: Message,
    guild_id: str = Path(..., description="Discord Guild ID"),
    message_id: str = Path(..., description="Discord Message ID"),
    _: None = Depends(require_permission),
):
    """Update a specific message"""
    ids = ids_string_to_int(guild_id=guild_id, message_id=message_id)
    guild_id_int, message_id_int = ids if isinstance(ids, tuple) else (ids, ids)

    try:
        message = await Messages.get_by(guild_id=guild_id_int, id=message_id_int)
        raise_404_if_not_found(message)

        created = await manage_message_state_change(
            old_message=message, new_message=message_data
        )

        if not created:
            if not message_data.published:
                message_data.message_id = None

            update_data = message_data.model_dump(
                exclude={"id", "guild_id", "updated_at"}
            )
            await message.update(**update_data)
            return message.to_dict()

        message = await message.refresh_until_message_id()
        if message.message_id is None:
            message.published = False
        return message.to_dict()

    except HTTPException:
        raise
    except Exception as e:
        raise _handle_database_error("update message", e)


@router.delete("/{guild_id}/messages/{message_id}")
async def delete_message(
    guild_id: str = Path(..., description="Discord Guild ID"),
    message_id: str = Path(..., description="Discord Message ID"),
    _: None = Depends(require_permission),
):
    """Delete a specific message"""
    ids = ids_string_to_int(guild_id=guild_id, message_id=message_id)
    guild_id_int, message_id_int = ids if isinstance(ids, tuple) else (ids, ids)

    try:
        message = await Messages.get_by(guild_id=guild_id_int, id=message_id_int)
        raise_404_if_not_found(message)

        await manage_message_state_change(
            old_message=message,
            new_message=None,
        )

        await message.delete()

        logger.info(f"Deleted message {message_id} for guild {guild_id}")
        return {"message": "Message deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise _handle_database_error("delete message", e)
