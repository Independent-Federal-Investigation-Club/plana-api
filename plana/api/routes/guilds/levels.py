from fastapi import APIRouter, Depends, HTTPException, Path, Request

from plana.api.middleware.utils import require_permission
from plana.api.utils.handler import handle_guild_config_refresh, raise_404_if_not_found
from plana.api.utils.helper import (
    _handle_database_error,
    ids_string_to_int,
)
from plana.database.models.levels import LevelSetting, LevelSettings

router = APIRouter()


@router.get("/{guild_id}/levels")
async def get_guild_level_config(
    guild_id: str = Path(..., description="Discord Guild ID"),
    _: None = Depends(require_permission),
):
    """Get guild level configuration"""
    guild_id_int = ids_string_to_int(guild_id=guild_id)

    try:
        level_config = await LevelSettings.get_by(id=guild_id_int)
        raise_404_if_not_found(level_config)

        return level_config.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise _handle_database_error("fetch guild level config", e)


@router.post("/{guild_id}/levels")
async def create_guild_level_config(
    level_data: LevelSetting,
    guild_id: str = Path(..., description="Discord Guild ID"),
    _: None = Depends(require_permission),
):
    """Create guild level configuration"""
    guild_id_int = ids_string_to_int(guild_id=guild_id)

    try:
        existing_config = await LevelSettings.get_by(id=guild_id_int)
        if existing_config:
            raise HTTPException(
                status_code=400,
                detail=f"Level configuration already exists for guild {guild_id}",
            )

        create_data = level_data.model_dump(exclude={"id"})
        level_config = LevelSettings(id=guild_id_int, **create_data)

        await level_config.save()
        return level_config.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise _handle_database_error("create guild level config", e)


@router.put("/{guild_id}/levels")
@router.patch("/{guild_id}/levels")
async def update_guild_level_config(
    request: Request,
    level_data: LevelSetting,
    guild_id: str = Path(..., description="Discord Guild ID"),
    _: None = Depends(require_permission),
):
    """Update guild level configuration"""
    guild_id_int = ids_string_to_int(guild_id=guild_id)

    try:
        level_config = await LevelSettings.get_by(id=guild_id_int)
        raise_404_if_not_found(level_config)

        if request.method == "PUT":
            # For PUT, we replace the entire configuration
            update_data = level_data.model_dump(exclude={"id"})
        else:
            # Only update fields that are provided in the PATCH request
            update_data = level_data.model_dump(exclude={"id"}, exclude_unset=True)

        await level_config.update(**update_data)
        await handle_guild_config_refresh(guild_id_int, "levels")
        return level_config.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise _handle_database_error("update guild level config", e)


@router.delete("/{guild_id}/levels")
async def delete_guild_level_config(
    guild_id: str = Path(..., description="Discord Guild ID"),
    _: None = Depends(require_permission),
):
    """Delete guild level configuration"""
    guild_id_int = ids_string_to_int(guild_id=guild_id)

    try:
        level_config = await LevelSettings.get_by(id=guild_id_int)
        raise_404_if_not_found(level_config)

        await level_config.delete()
        # Notify the bot about the new levels configuration
        await handle_guild_config_refresh(guild_id_int, "levels")
        return {"message": "Level configuration deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise _handle_database_error("delete guild level config", e)
