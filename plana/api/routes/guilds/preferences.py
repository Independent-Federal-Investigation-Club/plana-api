from loguru import logger
from fastapi import APIRouter, Depends, HTTPException, Path, Request

from plana.api.middleware.utils import require_permission
from plana.api.utils.helper import (
    _handle_database_error,
    ids_string_to_int,
)
from plana.api.utils.handler import raise_404_if_not_found, handle_guild_config_refresh
from plana.database.models.guild import GuildPreferences, GuildPreference


router = APIRouter()


@router.get("/{guild_id}/preferences")
async def get_guild_preferences(
    guild_id: str = Path(..., description="Discord Guild ID"),
    _: None = Depends(require_permission),
):
    """Get guild preferences"""
    guild_id_int = ids_string_to_int(guild_id=guild_id)

    try:
        prefs = await GuildPreferences.get_by(id=guild_id_int)
        raise_404_if_not_found(prefs)

        return prefs.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise _handle_database_error("fetch guild preferences", e)


@router.post("/{guild_id}/preferences")
async def create_guild_preferences(
    preferences: GuildPreference,
    guild_id: str = Path(..., description="Discord Guild ID"),
    _: None = Depends(require_permission),
):
    """Create guild preferences"""
    guild_id_int = ids_string_to_int(guild_id=guild_id)

    try:
        existing_prefs = await GuildPreferences.get_by(id=guild_id_int)
        if existing_prefs:
            raise HTTPException(
                status_code=400,
                detail=f"Preferences already exist for guild {guild_id}",
            )

        create_data = preferences.model_dump(exclude={"id"})
        prefs = GuildPreferences(id=guild_id_int, **create_data)

        await prefs.save()
        return prefs.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise _handle_database_error("create guild preferences", e)


@router.put("/{guild_id}/preferences")
@router.patch("/{guild_id}/preferences")
async def update_guild_preferences(
    request: Request,
    preferences: GuildPreference,
    guild_id: str = Path(..., description="Discord Guild ID"),
    _: None = Depends(require_permission),
):
    """Update guild preferences"""
    logger.info(
        f"Updating guild preferences for guild {guild_id} with data: {preferences}"
    )
    guild_id_int = ids_string_to_int(guild_id=guild_id)

    try:
        prefs = await GuildPreferences.get_by(id=guild_id_int)
        raise_404_if_not_found(prefs)

        if request.method == "PUT":
            update_data = preferences.model_dump(exclude={"id"})
        else:
            update_data = preferences.model_dump(exclude={"id"}, exclude_unset=True)

        await prefs.update(**update_data)

        await handle_guild_config_refresh(guild_id_int, "preferences")
        return prefs.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise _handle_database_error("update guild preferences", e)


@router.delete("/{guild_id}/preferences")
async def delete_guild_preferences(
    guild_id: str = Path(..., description="Discord Guild ID"),
    _: None = Depends(require_permission),
):
    """Delete guild preferences"""
    guild_id_int = ids_string_to_int(guild_id=guild_id)

    try:
        prefs = await GuildPreferences.get_by(id=guild_id_int)
        raise_404_if_not_found(prefs)

        await prefs.delete()
        logger.info(f"Deleted guild preferences for guild {guild_id}")

        return {"message": "Guild preferences deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise _handle_database_error("delete guild preferences", e)
