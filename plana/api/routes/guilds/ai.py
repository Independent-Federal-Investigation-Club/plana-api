from fastapi import APIRouter, Depends, HTTPException, Path, Request

from plana.api.middleware.utils import require_permission
from plana.api.utils.helper import (
    _handle_database_error,
    ids_string_to_int,
)
from plana.api.utils.handler import raise_404_if_not_found, handle_guild_config_refresh
from plana.database.models.ai import AISetting, AISettings


router = APIRouter()


@router.get("/{guild_id}/ai")
async def get_guild_ai_config(
    guild_id: str = Path(..., description="Discord Guild ID"),
    _: None = Depends(require_permission),
):
    """Get guild AI configuration"""
    guild_id_int = ids_string_to_int(guild_id=guild_id)

    try:
        ai_config = await AISettings.get_by(id=guild_id_int)
        raise_404_if_not_found(ai_config)

        return ai_config.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise _handle_database_error("fetch guild AI config", e)


@router.post("/{guild_id}/ai")
async def create_guild_ai_config(
    ai_data: AISetting,
    guild_id: str = Path(..., description="Discord Guild ID"),
    _: None = Depends(require_permission),
):
    """Create guild AI configuration"""
    guild_id_int = ids_string_to_int(guild_id=guild_id)

    try:
        existing_config = await AISettings.get_by(id=guild_id_int)
        if existing_config:
            raise HTTPException(
                status_code=400,
                detail=f"AI configuration already exists for guild {guild_id}",
            )

        create_data = ai_data.model_dump(exclude={"id"})
        ai_config = AISettings(id=guild_id_int, **create_data)

        await ai_config.save()
        return ai_config.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise _handle_database_error("create guild AI config", e)


@router.put("/{guild_id}/ai")
@router.patch("/{guild_id}/ai")
async def update_guild_ai_config(
    request: Request,
    ai_data: AISetting,
    guild_id: str = Path(..., description="Discord Guild ID"),
    _: None = Depends(require_permission),
):
    """Update guild AI configuration"""
    guild_id_int = ids_string_to_int(guild_id=guild_id)

    try:
        ai_config = await AISettings.get_by(id=guild_id_int)
        raise_404_if_not_found(ai_config)

        if request.method == "PUT":
            update_data = ai_data.model_dump(exclude={"id"})
        else:
            update_data = ai_data.model_dump(exclude={"id"}, exclude_unset=True)

        await ai_config.update(**update_data)
        await handle_guild_config_refresh(guild_id_int, "ai")
        return ai_config.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise _handle_database_error("update guild AI config", e)


@router.delete("/{guild_id}/ai")
async def delete_guild_ai_config(
    guild_id: str = Path(..., description="Discord Guild ID"),
    _: None = Depends(require_permission),
):
    """Delete guild AI configuration"""
    guild_id_int = ids_string_to_int(guild_id=guild_id)

    try:
        ai_config = await AISettings.get_by(id=guild_id_int)
        raise_404_if_not_found(ai_config)

        await ai_config.delete()
        return {"message": "AI configuration deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise _handle_database_error("delete guild AI config", e)
