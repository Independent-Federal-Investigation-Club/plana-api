from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Request
from loguru import logger

from plana.api.middleware.utils import require_permission
from plana.api.utils.handler import handle_guild_config_refresh, raise_404_if_not_found
from plana.api.utils.helper import (
    _handle_database_error,
    ids_string_to_int,
)
from plana.database.models.react_role import ReactRoles, ReactRoleSetting

router = APIRouter()


@router.get("/{guild_id}/react-roles")
async def list_guild_react_roles(
    guild_id: str = Path(..., description="Discord Guild ID"),
    limit: Optional[int] = Query(
        default=50, le=100, description="Maximum number of react roles to return"
    ),
    offset: Optional[int] = Query(
        default=0, ge=0, description="Number of react roles to skip"
    ),
    _: None = Depends(require_permission),
):
    """List all react roles for a guild"""
    guild_id_int = ids_string_to_int(guild_id=guild_id)

    try:
        react_roles = await ReactRoles.filter(
            ReactRoles.guild_id == guild_id_int,
            limit=limit,
            offset=offset,
            order_by=ReactRoles.updated_at.desc(),
        )
        total_count = await ReactRoles.count(ReactRoles.guild_id == guild_id_int)

        return {
            "data": [react_role.to_dict() for react_role in react_roles],
            "total_count": total_count,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise _handle_database_error("list guild react roles", e)


@router.post("/{guild_id}/react-roles")
async def create_guild_react_role(
    react_role_data: ReactRoleSetting,
    guild_id: str = Path(..., description="Discord Guild ID"),
    _: None = Depends(require_permission),
):
    """Create a new react role configuration for the guild"""
    guild_id_int = ids_string_to_int(guild_id=guild_id)
    try:
        existing_react_role = await ReactRoles.get_by(
            guild_id=guild_id_int, message_id=react_role_data.message_id
        )

        if existing_react_role:
            raise HTTPException(
                status_code=400,
                detail=f"React role configuration already exists for guild {guild_id} and message {react_role_data.message_id}",
            )

        create_data = react_role_data.model_dump(
            exclude={"id", "guild_id", "updated_at"}
        )
        react_role = ReactRoles(guild_id=guild_id_int, **create_data)

        await react_role.save()
        await handle_guild_config_refresh(guild_id_int, "react_roles")
        return react_role.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise _handle_database_error("create guild react role", e)


@router.get("/{guild_id}/react-roles/{react_role_id}")
async def get_guild_react_role(
    guild_id: str = Path(..., description="Discord Guild ID"),
    react_role_id: str = Path(..., description="React Role ID"),
    _: None = Depends(require_permission),
):
    """Get guild react-roles"""
    ids = ids_string_to_int(guild_id=guild_id, react_role_id=react_role_id)
    guild_id_int, react_role_id_int = ids if isinstance(ids, tuple) else (ids, ids)

    try:
        react_role = await ReactRoles.get_by(
            id=react_role_id_int, guild_id=guild_id_int
        )
        raise_404_if_not_found(react_role)

        return react_role.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise _handle_database_error("fetch guild react-roles", e)


@router.put("/{guild_id}/react-roles/{react_role_id}")
@router.patch("/{guild_id}/react-roles/{react_role_id}")
async def update_guild_react_role(
    request: Request,
    react_role_data: ReactRoleSetting,
    guild_id: str = Path(..., description="Discord Guild ID"),
    react_role_id: str = Path(..., description="React Role ID"),
    _: None = Depends(require_permission),
):
    """Update a guild react role configuration"""
    ids = ids_string_to_int(guild_id=guild_id, react_role_id=react_role_id)
    guild_id_int, react_role_id_int = ids if isinstance(ids, tuple) else (ids, ids)

    try:
        react_role = await ReactRoles.get_by(
            id=react_role_id_int, guild_id=guild_id_int
        )
        raise_404_if_not_found(react_role)

        if request.method == "PUT":
            update_data = react_role_data.model_dump(
                exclude={"id", "guild_id", "updated_at"}
            )
        else:
            update_data = react_role_data.model_dump(
                {"id", "guild_id", "updated_at"}, exclude_unset=True
            )

        await react_role.update(**update_data)
        await handle_guild_config_refresh(guild_id_int, "react_roles")
        return react_role.to_dict()
    except HTTPException:
        raise
    except Exception as e:
        raise _handle_database_error("update guild react role", e)


@router.delete("/{guild_id}/react-roles/{react_role_id}")
async def delete_guild_react_role(
    guild_id: str = Path(..., description="Discord Guild ID"),
    react_role_id: str = Path(..., description="React Role ID"),
    _: None = Depends(require_permission),
):
    """Delete a guild react role configuration"""
    ids = ids_string_to_int(guild_id=guild_id, react_role_id=react_role_id)
    guild_id_int, react_role_id_int = ids if isinstance(ids, tuple) else (ids, ids)

    try:
        react_role = await ReactRoles.get_by(
            id=react_role_id_int, guild_id=guild_id_int
        )
        raise_404_if_not_found(react_role)

        await react_role.delete()
        await handle_guild_config_refresh(guild_id_int, "react_roles")
        return {"message": "React role deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise _handle_database_error("delete guild react role", e)
