from fastapi import APIRouter, Depends, HTTPException, Path, Request
from loguru import logger

from plana.api.middleware.utils import bot_only_operation, require_permission
from plana.api.utils.handler import raise_404_if_not_found
from plana.api.utils.helper import (
    _handle_database_error,
    ids_string_to_int,
)
from plana.database.models.core import Guild, Guilds

router = APIRouter()


@router.get("/{guild_id}/data")
async def get_guild_data(
    guild_id: str = Path(..., description="Discord Guild ID"),
    _: None = Depends(require_permission),
):
    """Get guild data"""
    guild_id_int = ids_string_to_int(guild_id=guild_id)

    try:
        guild = await Guilds.get_by(id=guild_id_int)
        raise_404_if_not_found(guild)

        return guild.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise _handle_database_error("fetch guild data", e)


@router.post("/{guild_id}/data")
async def create_guild_data(
    guild: Guild,
    guild_id: str = Path(..., description="Discord Guild ID"),
    _: None = Depends(bot_only_operation),
):
    """Create a new guild"""
    guild_id_int = ids_string_to_int(guild_id=guild_id)
    try:
        if await Guilds.get_by(id=guild.id):
            raise HTTPException(
                status_code=400,
                detail=f"Guild with ID {guild.id} already exists",
            )

        create_data = guild.model_dump(exclude={"id"})
        guild = Guilds(id=guild_id_int, **create_data)

        await guild.save()
        return guild.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise _handle_database_error("create guild", e)


@router.patch("/{guild_id}/data")
@router.put("/{guild_id}/data")
async def update_guild_data(
    request: Request,
    guild: Guild,
    guild_id: str = Path(..., description="Discord Guild ID"),
    _: None = Depends(bot_only_operation),
):
    """Update an existing guild"""
    guild_id_int = ids_string_to_int(guild_id=guild_id)

    try:
        guild_data = await Guilds.get_by(id=guild_id_int)
        raise_404_if_not_found(guild_data)

        if request.method == "PUT":
            # For PUT, we replace the entire configuration
            update_data = guild.model_dump(exclude={"id"})
        else:
            # Only update fields that are provided in the PATCH request
            update_data = guild.model_dump(exclude={"id"}, exclude_unset=True)

        await guild_data.update(**update_data)
        return guild_data.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise _handle_database_error("update guild", e)


@router.delete("/{guild_id}/data")
async def delete_guild_data(
    guild_id: str = Path(..., description="Discord Guild ID"),
    _: None = Depends(bot_only_operation),
):
    """Delete a guild"""
    guild_id_int = ids_string_to_int(guild_id=guild_id)

    try:
        guild_data = await Guilds.get_by(id=guild_id_int)
        raise_404_if_not_found(guild_data)

        await guild_data.delete()
        logger.info(f"Deleted guild {guild_id}")

        return {"message": "Guild deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise _handle_database_error("delete guild", e)
