from loguru import logger
from fastapi import APIRouter, Depends, HTTPException, Path, Request

from plana.api.middleware.utils import require_permission
from plana.api.utils.helper import (
    _handle_database_error,
    ids_string_to_int,
)
from plana.api.utils.handler import raise_404_if_not_found, handle_guild_config_refresh
from plana.database.models.welcome import WelcomeSetting, WelcomeSettings


router = APIRouter()


@router.get("/{guild_id}/welcome")
async def get_guild_welcome_config(
    guild_id: str = Path(..., description="Discord Guild ID"),
    _: None = Depends(require_permission),
):
    """Get guild welcome configuration"""
    guild_id_int = ids_string_to_int(guild_id=guild_id)

    try:
        welcome_config = await WelcomeSettings.get_by(id=guild_id_int)
        raise_404_if_not_found(welcome_config)

        return welcome_config.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise _handle_database_error("fetch guild welcome config", e)


@router.post("/{guild_id}/welcome")
async def create_guild_welcome_config(
    welcome_data: WelcomeSetting,
    guild_id: str = Path(..., description="Discord Guild ID"),
    _: None = Depends(require_permission),
):
    """Create guild welcome configuration"""
    guild_id_int = ids_string_to_int(guild_id=guild_id)

    try:
        existing_config = await WelcomeSettings.get_by(id=guild_id_int)
        if existing_config:
            raise HTTPException(
                status_code=400,
                detail=f"Welcome configuration already exists for guild {guild_id}",
            )

        create_data = welcome_data.model_dump(exclude={"id"})
        welcome_config = WelcomeSettings(id=guild_id_int, **create_data)

        await welcome_config.save()
        return welcome_config.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise _handle_database_error("create guild welcome config", e)


@router.put("/{guild_id}/welcome")
@router.patch("/{guild_id}/welcome")
async def update_guild_welcome_config(
    request: Request,
    welcome_data: WelcomeSetting,
    guild_id: str = Path(..., description="Discord Guild ID"),
    _: None = Depends(require_permission),
):
    """Update guild welcome configuration"""
    guild_id_int = ids_string_to_int(guild_id=guild_id)

    try:
        welcome_config = await WelcomeSettings.get_by(id=guild_id_int)
        raise_404_if_not_found(welcome_config)

        if request.method == "PUT":
            update_data = welcome_data.model_dump(exclude={"id", "updated_at"})
        else:
            update_data = welcome_data.model_dump(
                exclude={"id", "updated_at"}, exclude_unset=True
            )

        await welcome_config.update(**update_data)
        await handle_guild_config_refresh(guild_id_int, "welcome")
        return welcome_config.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise _handle_database_error("update guild welcome config", e)


@router.delete("/{guild_id}/welcome")
async def delete_guild_welcome_config(
    guild_id: str = Path(..., description="Discord Guild ID"),
    _: None = Depends(require_permission),
):
    """Delete guild welcome configuration"""
    guild_id_int = ids_string_to_int(guild_id=guild_id)

    try:
        welcome_config = await WelcomeSettings.get_by(id=guild_id_int)
        raise_404_if_not_found(welcome_config)

        await welcome_config.delete()
        return {"message": "Welcome configuration deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise _handle_database_error("delete guild welcome config", e)
